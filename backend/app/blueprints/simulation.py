"""
Simulation blueprint for Monte Carlo cyber risk simulation management.

This module provides endpoints for creating, running, monitoring, and retrieving
simulation results with real-time progress updates via WebSocket.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit, join_room, leave_room
from marshmallow import Schema, fields, ValidationError, validates
import uuid
import structlog
from typing import Dict, Any

from app import db, socketio
from app.models import User, SimulationRun, SimulationResult, Portfolio
from app.simulation import (
    SimulationEngine, SimulationParameters, EventParameters,
    DistributionFactory, ParameterError, SimulationError
)

logger = structlog.get_logger(__name__)

# Create the simulation blueprint
simulation_bp = Blueprint('simulation', __name__)


# Validation schemas
class EventParametersSchema(Schema):
    """Schema for event parameters validation."""
    
    frequency_distribution = fields.Str(required=True, validate=lambda x: x in ['poisson', 'negative_binomial', 'binomial'])
    frequency_params = fields.Dict(required=True)
    severity_distribution = fields.Str(required=True, validate=lambda x: x in ['lognormal', 'pareto', 'gamma', 'exponential', 'weibull'])
    severity_params = fields.Dict(required=True)
    correlation_enabled = fields.Bool(missing=False)
    correlation_params = fields.Dict(missing=dict)


class SimulationRequestSchema(Schema):
    """Schema for simulation request validation."""
    
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    description = fields.Str(missing="")
    num_iterations = fields.Int(required=True, validate=lambda x: 1 <= x <= 10_000_000)
    random_seed = fields.Int(missing=None, allow_none=True)
    event_params = fields.Nested(EventParametersSchema, required=True)
    portfolio_id = fields.Str(missing=None, allow_none=True)
    
    # Financial calculation parameters
    apply_deductibles = fields.Bool(missing=True)
    apply_limits = fields.Bool(missing=True)
    apply_reinsurance = fields.Bool(missing=False)
    reinsurance_config = fields.Dict(missing=dict)
    
    # Simulation control parameters
    max_events_per_iteration = fields.Int(missing=100, validate=lambda x: 1 <= x <= 10000)
    convergence_check = fields.Bool(missing=False)
    convergence_threshold = fields.Float(missing=0.001, validate=lambda x: x > 0)
    convergence_window = fields.Int(missing=1000, validate=lambda x: x > 0)
    
    # Performance parameters
    batch_size = fields.Int(missing=1000, validate=lambda x: x > 0)
    parallel_processing = fields.Bool(missing=True)
    max_workers = fields.Int(missing=None, allow_none=True, validate=lambda x: x is None or x > 0)
    
    # Output parameters
    save_raw_losses = fields.Bool(missing=False)
    calculate_percentiles = fields.Bool(missing=True)
    percentile_levels = fields.List(fields.Float(validate=lambda x: 0 <= x <= 1), missing=[0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999])


# Initialize schemas
simulation_request_schema = SimulationRequestSchema()


@simulation_bp.route('/run', methods=['POST'])
@jwt_required()
def run_simulation():
    """
    Start a new simulation run.
    
    Expected JSON payload:
    {
        "name": "Simulation Name",
        "description": "Optional description",
        "num_iterations": 10000,
        "random_seed": 12345,
        "event_params": {
            "frequency_distribution": "poisson",
            "frequency_params": {"lambda": 2.5},
            "severity_distribution": "lognormal",
            "severity_params": {"mu": 10, "sigma": 1.5}
        },
        "portfolio_id": "uuid-string" // optional
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validated_data = simulation_request_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Validate portfolio if specified
        portfolio = None
        if validated_data.get('portfolio_id'):
            portfolio = Portfolio.query.filter_by(
                id=validated_data['portfolio_id'],
                user_id=current_user_id
            ).first()
            if not portfolio:
                return jsonify({'error': 'Portfolio not found'}), 404
        
        # Create simulation run record
        simulation_run = SimulationRun(
            user_id=current_user_id,
            portfolio_id=validated_data.get('portfolio_id'),
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            num_iterations=validated_data['num_iterations'],
            random_seed=validated_data.get('random_seed'),
            event_parameters=validated_data['event_params'],
            simulation_config={
                'apply_deductibles': validated_data.get('apply_deductibles', True),
                'apply_limits': validated_data.get('apply_limits', True),
                'apply_reinsurance': validated_data.get('apply_reinsurance', False),
                'reinsurance_config': validated_data.get('reinsurance_config', {}),
                'max_events_per_iteration': validated_data.get('max_events_per_iteration', 100),
                'convergence_check': validated_data.get('convergence_check', False),
                'convergence_threshold': validated_data.get('convergence_threshold', 0.001),
                'convergence_window': validated_data.get('convergence_window', 1000),
                'batch_size': validated_data.get('batch_size', 1000),
                'parallel_processing': validated_data.get('parallel_processing', True),
                'max_workers': validated_data.get('max_workers'),
                'save_raw_losses': validated_data.get('save_raw_losses', False),
                'calculate_percentiles': validated_data.get('calculate_percentiles', True),
                'percentile_levels': validated_data.get('percentile_levels', [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999])
            },
            status='pending'
        )
        
        db.session.add(simulation_run)
        db.session.commit()
        
        # Start the simulation asynchronously
        socketio.start_background_task(
            target=_run_simulation_background,
            simulation_run_id=str(simulation_run.id),
            user_id=current_user_id
        )
        
        logger.info("Simulation started", simulation_id=str(simulation_run.id), user_id=current_user_id)
        
        return jsonify({
            'message': 'Simulation started successfully',
            'simulation_id': str(simulation_run.id),
            'simulation': simulation_run.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to start simulation", error=str(e))
        return jsonify({'error': 'Failed to start simulation', 'message': str(e)}), 500


def _run_simulation_background(simulation_run_id: str, user_id: str):
    """Run simulation in background with progress updates."""
    try:
        with current_app.app_context():
            # Get the simulation run
            simulation_run = SimulationRun.query.get(simulation_run_id)
            if not simulation_run:
                logger.error("Simulation run not found", simulation_id=simulation_run_id)
                return
            
            # Update status to running
            simulation_run.status = 'running'
            simulation_run.started_at = datetime.now(timezone.utc)
            db.session.commit()
            
            # Emit status update
            socketio.emit('simulation_status', {
                'simulation_id': simulation_run_id,
                'status': 'running',
                'message': 'Simulation started'
            }, room=f'user_{user_id}')
            
            # Create progress callback
            def progress_callback(current_iteration: int, total_iterations: int):
                progress_percent = (current_iteration / total_iterations) * 100
                simulation_run.progress_percent = progress_percent
                simulation_run.current_iteration = current_iteration
                db.session.commit()
                
                # Emit progress update every 1000 iterations or at 100%
                if current_iteration % 1000 == 0 or current_iteration == total_iterations:
                    socketio.emit('simulation_progress', {
                        'simulation_id': simulation_run_id,
                        'progress_percent': progress_percent,
                        'current_iteration': current_iteration,
                        'total_iterations': total_iterations
                    }, room=f'user_{user_id}')
            
            # Create simulation parameters
            event_params = EventParameters(
                frequency_distribution=simulation_run.event_parameters['frequency_distribution'],
                frequency_params=simulation_run.event_parameters['frequency_params'],
                severity_distribution=simulation_run.event_parameters['severity_distribution'],
                severity_params=simulation_run.event_parameters['severity_params'],
                correlation_enabled=simulation_run.event_parameters.get('correlation_enabled', False),
                correlation_params=simulation_run.event_parameters.get('correlation_params', {})
            )
            
            sim_params = SimulationParameters(
                num_iterations=simulation_run.num_iterations,
                random_seed=simulation_run.random_seed,
                event_params=event_params,
                portfolio_id=str(simulation_run.portfolio_id) if simulation_run.portfolio_id else None,
                **simulation_run.simulation_config
            )
            
            # Create and run simulation
            engine = SimulationEngine(progress_callback=progress_callback)
            
            # Get portfolio policies if needed
            portfolio_policies = None
            if simulation_run.portfolio_id:
                portfolio = Portfolio.query.get(simulation_run.portfolio_id)
                if portfolio:
                    # Convert portfolio policies to PolicyTerms
                    # This would need to be implemented based on your Portfolio/Policy models
                    portfolio_policies = _convert_portfolio_to_policy_terms(portfolio)
            
            # Run the simulation
            results = engine.run_simulation(sim_params, portfolio_policies)
            
            # Save results to database
            risk_metrics = results['risk_metrics']
            
            simulation_result = SimulationResult(
                simulation_run_id=simulation_run.id,
                expected_loss=risk_metrics['expected_loss'],
                var_95=risk_metrics['var_95'],
                var_99=risk_metrics['var_99'],
                var_99_9=risk_metrics['var_99_9'],
                tvar_95=risk_metrics['tvar_95'],
                tvar_99=risk_metrics['tvar_99'],
                tvar_99_9=risk_metrics['tvar_99_9'],
                min_loss=risk_metrics['minimum_loss'],
                max_loss=risk_metrics['maximum_loss'],
                std_deviation=risk_metrics['standard_deviation'],
                skewness=risk_metrics['skewness'],
                kurtosis=risk_metrics['kurtosis'],
                probability_of_loss=risk_metrics['probability_of_loss'],
                loss_distribution=risk_metrics.get('histogram_data'),
                percentiles=risk_metrics.get('percentiles'),
                exceedance_probabilities=risk_metrics.get('exceedance_curve')
            )
            
            db.session.add(simulation_result)
            
            # Update simulation run status
            simulation_run.status = 'completed'
            simulation_run.completed_at = datetime.now(timezone.utc)
            simulation_run.progress_percent = 100.0
            
            db.session.commit()
            
            # Emit completion notification
            socketio.emit('simulation_complete', {
                'simulation_id': simulation_run_id,
                'status': 'completed',
                'message': 'Simulation completed successfully',
                'results_summary': {
                    'expected_loss': risk_metrics['expected_loss'],
                    'var_99': risk_metrics['var_99'],
                    'execution_time': results['execution_time']
                }
            }, room=f'user_{user_id}')
            
            logger.info("Simulation completed successfully", simulation_id=simulation_run_id)
            
    except Exception as e:
        logger.error("Simulation failed", simulation_id=simulation_run_id, error=str(e))
        
        # Update simulation status to failed
        try:
            with current_app.app_context():
                simulation_run = SimulationRun.query.get(simulation_run_id)
                if simulation_run:
                    simulation_run.status = 'failed'
                    simulation_run.error_message = str(e)
                    simulation_run.completed_at = datetime.now(timezone.utc)
                    db.session.commit()
                
                # Emit failure notification
                socketio.emit('simulation_error', {
                    'simulation_id': simulation_run_id,
                    'status': 'failed',
                    'error': str(e)
                }, room=f'user_{user_id}')
        except Exception as db_error:
            logger.error("Failed to update simulation status", error=str(db_error))


def _convert_portfolio_to_policy_terms(portfolio):
    """Convert Portfolio model to PolicyTerms for simulation."""
    # This is a placeholder - implement based on your Portfolio/Policy models
    from app.simulation.financial import PolicyTerms
    
    policy_terms = {}
    for policy in portfolio.policies:
        policy_terms[str(policy.id)] = PolicyTerms(
            policy_id=str(policy.id),
            coverage_limit=policy.coverage_limit,
            deductible=policy.deductible,
            sub_limits=policy.sub_limits,
            coinsurance=0.0,  # Add this field to Policy model if needed
            waiting_period=0,  # Add this field to Policy model if needed
            policy_aggregate=None  # Add this field to Policy model if needed
        )
    
    return policy_terms


@simulation_bp.route('/list', methods=['GET'])
@jwt_required()
def list_simulations():
    """
    List user's simulation runs with optional filtering.
    
    Query parameters:
    - status: Filter by status (pending, running, completed, failed)
    - limit: Maximum number of results (default: 50)
    - offset: Number of results to skip (default: 0)
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        status = request.args.get('status')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = SimulationRun.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Apply pagination
        query = query.order_by(SimulationRun.created_at.desc())
        total_count = query.count()
        simulations = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'simulations': [sim.to_dict() for sim in simulations],
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }), 200
        
    except Exception as e:
        logger.error("Failed to list simulations", error=str(e))
        return jsonify({'error': 'Failed to retrieve simulations'}), 500


@simulation_bp.route('/<simulation_id>', methods=['GET'])
@jwt_required()
def get_simulation(simulation_id: str):
    """Get detailed information about a specific simulation run."""
    try:
        current_user_id = get_jwt_identity()
        
        simulation = SimulationRun.query.filter_by(
            id=simulation_id,
            user_id=current_user_id
        ).first()
        
        if not simulation:
            return jsonify({'error': 'Simulation not found'}), 404
        
        result = simulation.to_dict()
        
        # Include results if available
        if simulation.results:
            result['results'] = simulation.results.to_dict()
        
        return jsonify({'simulation': result}), 200
        
    except Exception as e:
        logger.error("Failed to get simulation", error=str(e))
        return jsonify({'error': 'Failed to retrieve simulation'}), 500


@simulation_bp.route('/<simulation_id>/results', methods=['GET'])
@jwt_required()
def get_simulation_results(simulation_id: str):
    """Get detailed results for a completed simulation."""
    try:
        current_user_id = get_jwt_identity()
        
        simulation = SimulationRun.query.filter_by(
            id=simulation_id,
            user_id=current_user_id
        ).first()
        
        if not simulation:
            return jsonify({'error': 'Simulation not found'}), 404
        
        if simulation.status != 'completed':
            return jsonify({'error': 'Simulation not completed yet'}), 400
        
        if not simulation.results:
            return jsonify({'error': 'No results available'}), 404
        
        return jsonify({
            'simulation_id': simulation_id,
            'results': simulation.results.to_dict()
        }), 200
        
    except Exception as e:
        logger.error("Failed to get simulation results", error=str(e))
        return jsonify({'error': 'Failed to retrieve results'}), 500


@simulation_bp.route('/<simulation_id>/stop', methods=['POST'])
@jwt_required()
def stop_simulation(simulation_id: str):
    """Stop a running simulation."""
    try:
        current_user_id = get_jwt_identity()
        
        simulation = SimulationRun.query.filter_by(
            id=simulation_id,
            user_id=current_user_id
        ).first()
        
        if not simulation:
            return jsonify({'error': 'Simulation not found'}), 404
        
        if simulation.status not in ['pending', 'running']:
            return jsonify({'error': 'Simulation cannot be stopped'}), 400
        
        # Update status
        simulation.status = 'cancelled'
        simulation.error_message = 'Stopped by user'
        simulation.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Emit stop notification
        socketio.emit('simulation_stopped', {
            'simulation_id': simulation_id,
            'status': 'cancelled',
            'message': 'Simulation stopped by user'
        }, room=f'user_{current_user_id}')
        
        return jsonify({'message': 'Simulation stopped successfully'}), 200
        
    except Exception as e:
        logger.error("Failed to stop simulation", error=str(e))
        return jsonify({'error': 'Failed to stop simulation'}), 500


@simulation_bp.route('/<simulation_id>', methods=['DELETE'])
@jwt_required()
def delete_simulation(simulation_id: str):
    """Delete a simulation run and its results."""
    try:
        current_user_id = get_jwt_identity()
        
        simulation = SimulationRun.query.filter_by(
            id=simulation_id,
            user_id=current_user_id
        ).first()
        
        if not simulation:
            return jsonify({'error': 'Simulation not found'}), 404
        
        # Don't allow deletion of running simulations
        if simulation.status == 'running':
            return jsonify({'error': 'Cannot delete running simulation'}), 400
        
        # Delete simulation and related results (cascade will handle this)
        db.session.delete(simulation)
        db.session.commit()
        
        return jsonify({'message': 'Simulation deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to delete simulation", error=str(e))
        return jsonify({'error': 'Failed to delete simulation'}), 500


@simulation_bp.route('/distributions', methods=['GET'])
def get_available_distributions():
    """Get list of available frequency and severity distributions."""
    try:
        distributions = DistributionFactory.get_available_distributions()
        
        return jsonify({
            'distributions': distributions,
            'parameter_schemas': {
                'frequency': {
                    'poisson': {'lambda': 'Poisson rate parameter (λ > 0)'},
                    'negative_binomial': {
                        'n': 'Number of successes (n > 0)',
                        'p': 'Probability of success (0 < p ≤ 1)'
                    },
                    'binomial': {
                        'n': 'Number of trials (n > 0, integer)',
                        'p': 'Probability of success (0 ≤ p ≤ 1)'
                    }
                },
                'severity': {
                    'lognormal': {
                        'mu': 'Log-scale parameter (μ)',
                        'sigma': 'Log-shape parameter (σ > 0)'
                    },
                    'pareto': {
                        'scale': 'Scale parameter (> 0)',
                        'shape': 'Shape parameter (> 0)'
                    },
                    'gamma': {
                        'shape': 'Shape parameter (> 0)',
                        'scale': 'Scale parameter (> 0)'
                    },
                    'exponential': {
                        'scale': 'Scale parameter (> 0)'
                    },
                    'weibull': {
                        'shape': 'Shape parameter (> 0)',
                        'scale': 'Scale parameter (> 0)'
                    }
                }
            }
        }), 200
        
    except Exception as e:
        logger.error("Failed to get distributions", error=str(e))
        return jsonify({'error': 'Failed to retrieve distributions'}), 500


# WebSocket events for real-time updates
@socketio.on('join_simulation_room')
def on_join_simulation_room(data):
    """Join room for simulation updates."""
    try:
        user_id = get_jwt_identity()
        if user_id:
            join_room(f'user_{user_id}')
            emit('joined_room', {'room': f'user_{user_id}'})
    except Exception as e:
        logger.error("Failed to join simulation room", error=str(e))


@socketio.on('leave_simulation_room')
def on_leave_simulation_room(data):
    """Leave room for simulation updates."""
    try:
        user_id = get_jwt_identity()
        if user_id:
            leave_room(f'user_{user_id}')
            emit('left_room', {'room': f'user_{user_id}'})
    except Exception as e:
        logger.error("Failed to leave simulation room", error=str(e)) 