"""
Scenarios blueprint for managing simulation scenarios and scenario analysis.

This module provides endpoints for creating, managing, and comparing
different simulation scenarios for stress testing and analysis.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
import structlog

from app import db
from app.models import User, Scenario
from app.blueprints.simulation import EventParametersSchema

logger = structlog.get_logger(__name__)

# Create the scenarios blueprint
scenarios_bp = Blueprint('scenarios', __name__)


# Validation schemas
class ScenarioModificationSchema(Schema):
    """Schema for scenario modification parameters."""
    
    frequency_multiplier = fields.Float(missing=1.0, validate=lambda x: x > 0)
    severity_multiplier = fields.Float(missing=1.0, validate=lambda x: x > 0)
    frequency_additive = fields.Float(missing=0.0)
    severity_additive = fields.Float(missing=0.0)
    
    # Parameter-specific modifications
    frequency_param_modifications = fields.Dict(missing=dict)
    severity_param_modifications = fields.Dict(missing=dict)
    
    # Custom modifications
    custom_modifications = fields.Dict(missing=dict)


class ScenarioSchema(Schema):
    """Schema for scenario validation."""
    
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    description = fields.Str(missing="")
    base_parameters = fields.Nested(EventParametersSchema, required=True)
    modifications = fields.Nested(ScenarioModificationSchema, required=True)
    is_active = fields.Bool(missing=True)


class ScenarioUpdateSchema(Schema):
    """Schema for scenario update validation."""
    
    name = fields.Str(missing=None, validate=lambda x: x is None or len(x.strip()) > 0)
    description = fields.Str(missing=None)
    base_parameters = fields.Nested(EventParametersSchema, missing=None)
    modifications = fields.Nested(ScenarioModificationSchema, missing=None)
    is_active = fields.Bool(missing=None)


# Initialize schemas
scenario_schema = ScenarioSchema()
scenario_update_schema = ScenarioUpdateSchema()


@scenarios_bp.route('/', methods=['POST'])
@jwt_required()
def create_scenario():
    """
    Create a new simulation scenario.
    
    Expected JSON payload:
    {
        "name": "High Frequency Scenario",
        "description": "Scenario with increased event frequency",
        "base_parameters": {
            "frequency_distribution": "poisson",
            "frequency_params": {"lambda": 2.5},
            "severity_distribution": "lognormal",
            "severity_params": {"mu": 10, "sigma": 1.5}
        },
        "modifications": {
            "frequency_multiplier": 2.0,
            "severity_multiplier": 1.2
        }
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
            validated_data = scenario_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Check for duplicate scenario names
        existing_scenario = Scenario.query.filter_by(
            user_id=current_user_id,
            name=validated_data['name']
        ).first()
        
        if existing_scenario:
            return jsonify({'error': 'Scenario with this name already exists'}), 409
        
        # Create new scenario
        scenario = Scenario(
            user_id=current_user_id,
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            base_parameters=validated_data['base_parameters'],
            modifications=validated_data['modifications'],
            is_active=validated_data.get('is_active', True)
        )
        
        db.session.add(scenario)
        db.session.commit()
        
        logger.info("Scenario created", scenario_id=str(scenario.id), user_id=current_user_id)
        
        return jsonify({
            'message': 'Scenario created successfully',
            'scenario': scenario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to create scenario", error=str(e))
        return jsonify({'error': 'Failed to create scenario', 'message': str(e)}), 500


@scenarios_bp.route('/', methods=['GET'])
@jwt_required()
def list_scenarios():
    """
    List user's scenarios with optional filtering.
    
    Query parameters:
    - active_only: Filter to only active scenarios (true/false)
    - limit: Maximum number of results (default: 50)
    - offset: Number of results to skip (default: 0)
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        offset = int(request.args.get('offset', 0))
        
        # Build query
        query = Scenario.query.filter_by(user_id=current_user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        # Apply pagination
        query = query.order_by(Scenario.created_at.desc())
        total_count = query.count()
        scenarios = query.offset(offset).limit(limit).all()
        
        return jsonify({
            'scenarios': [scenario.to_dict() for scenario in scenarios],
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }), 200
        
    except Exception as e:
        logger.error("Failed to list scenarios", error=str(e))
        return jsonify({'error': 'Failed to retrieve scenarios'}), 500


@scenarios_bp.route('/<scenario_id>', methods=['GET'])
@jwt_required()
def get_scenario(scenario_id: str):
    """Get detailed information about a specific scenario."""
    try:
        current_user_id = get_jwt_identity()
        
        scenario = Scenario.query.filter_by(
            id=scenario_id,
            user_id=current_user_id
        ).first()
        
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        return jsonify({'scenario': scenario.to_dict()}), 200
        
    except Exception as e:
        logger.error("Failed to get scenario", error=str(e))
        return jsonify({'error': 'Failed to retrieve scenario'}), 500


@scenarios_bp.route('/<scenario_id>', methods=['PUT'])
@jwt_required()
def update_scenario(scenario_id: str):
    """
    Update a scenario.
    
    Expected JSON payload (all fields optional):
    {
        "name": "Updated Scenario Name",
        "description": "Updated description",
        "modifications": {
            "frequency_multiplier": 1.5
        }
    }
    """
    try:
        current_user_id = get_jwt_identity()
        
        scenario = Scenario.query.filter_by(
            id=scenario_id,
            user_id=current_user_id
        ).first()
        
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            validated_data = scenario_update_schema.load(json_data)
        except ValidationError as err:
            return jsonify({'error': 'Validation failed', 'details': err.messages}), 400
        
        # Check for duplicate scenario names if name is being changed
        if 'name' in validated_data and validated_data['name'] != scenario.name:
            existing_scenario = Scenario.query.filter_by(
                user_id=current_user_id,
                name=validated_data['name']
            ).first()
            
            if existing_scenario:
                return jsonify({'error': 'Scenario with this name already exists'}), 409
        
        # Update scenario fields
        if 'name' in validated_data:
            scenario.name = validated_data['name']
        if 'description' in validated_data:
            scenario.description = validated_data['description']
        if 'base_parameters' in validated_data:
            scenario.base_parameters = validated_data['base_parameters']
        if 'modifications' in validated_data:
            scenario.modifications = validated_data['modifications']
        if 'is_active' in validated_data:
            scenario.is_active = validated_data['is_active']
        
        scenario.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        logger.info("Scenario updated", scenario_id=str(scenario.id), user_id=current_user_id)
        
        return jsonify({
            'message': 'Scenario updated successfully',
            'scenario': scenario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to update scenario", error=str(e))
        return jsonify({'error': 'Failed to update scenario'}), 500


@scenarios_bp.route('/<scenario_id>', methods=['DELETE'])
@jwt_required()
def delete_scenario(scenario_id: str):
    """Delete a scenario."""
    try:
        current_user_id = get_jwt_identity()
        
        scenario = Scenario.query.filter_by(
            id=scenario_id,
            user_id=current_user_id
        ).first()
        
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        # Check if scenario is used in any simulations
        simulation_count = scenario.simulation_runs.count()
        if simulation_count > 0:
            return jsonify({
                'error': 'Cannot delete scenario',
                'message': f'Scenario is used in {simulation_count} simulation(s)'
            }), 409
        
        # Delete scenario
        db.session.delete(scenario)
        db.session.commit()
        
        logger.info("Scenario deleted", scenario_id=scenario_id, user_id=current_user_id)
        
        return jsonify({'message': 'Scenario deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to delete scenario", error=str(e))
        return jsonify({'error': 'Failed to delete scenario'}), 500


@scenarios_bp.route('/<scenario_id>/activate', methods=['POST'])
@jwt_required()
def activate_scenario(scenario_id: str):
    """Activate a scenario."""
    try:
        current_user_id = get_jwt_identity()
        
        scenario = Scenario.query.filter_by(
            id=scenario_id,
            user_id=current_user_id
        ).first()
        
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        scenario.is_active = True
        scenario.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({'message': 'Scenario activated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to activate scenario", error=str(e))
        return jsonify({'error': 'Failed to activate scenario'}), 500


@scenarios_bp.route('/<scenario_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_scenario(scenario_id: str):
    """Deactivate a scenario."""
    try:
        current_user_id = get_jwt_identity()
        
        scenario = Scenario.query.filter_by(
            id=scenario_id,
            user_id=current_user_id
        ).first()
        
        if not scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        scenario.is_active = False
        scenario.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({'message': 'Scenario deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to deactivate scenario", error=str(e))
        return jsonify({'error': 'Failed to deactivate scenario'}), 500


@scenarios_bp.route('/<scenario_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_scenario(scenario_id: str):
    """
    Duplicate a scenario with a new name.
    
    Expected JSON payload:
    {
        "name": "New Scenario Name"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        
        original_scenario = Scenario.query.filter_by(
            id=scenario_id,
            user_id=current_user_id
        ).first()
        
        if not original_scenario:
            return jsonify({'error': 'Scenario not found'}), 404
        
        # Validate request data
        json_data = request.get_json()
        if not json_data or 'name' not in json_data:
            return jsonify({'error': 'New scenario name is required'}), 400
        
        new_name = json_data['name'].strip()
        if not new_name:
            return jsonify({'error': 'Scenario name cannot be empty'}), 400
        
        # Check for duplicate scenario names
        existing_scenario = Scenario.query.filter_by(
            user_id=current_user_id,
            name=new_name
        ).first()
        
        if existing_scenario:
            return jsonify({'error': 'Scenario with this name already exists'}), 409
        
        # Create duplicate scenario
        new_scenario = Scenario(
            user_id=current_user_id,
            name=new_name,
            description=f"Copy of {original_scenario.name}",
            base_parameters=original_scenario.base_parameters.copy(),
            modifications=original_scenario.modifications.copy(),
            is_active=True
        )
        
        db.session.add(new_scenario)
        db.session.commit()
        
        logger.info("Scenario duplicated", 
                   original_id=scenario_id, 
                   new_id=str(new_scenario.id), 
                   user_id=current_user_id)
        
        return jsonify({
            'message': 'Scenario duplicated successfully',
            'scenario': new_scenario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to duplicate scenario", error=str(e))
        return jsonify({'error': 'Failed to duplicate scenario'}), 500


@scenarios_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_scenario_templates():
    """Get predefined scenario templates for common stress tests."""
    try:
        templates = [
            {
                'name': 'High Frequency Scenario',
                'description': 'Scenario with 2x increase in event frequency',
                'modifications': {
                    'frequency_multiplier': 2.0,
                    'severity_multiplier': 1.0
                }
            },
            {
                'name': 'High Severity Scenario',
                'description': 'Scenario with 1.5x increase in event severity',
                'modifications': {
                    'frequency_multiplier': 1.0,
                    'severity_multiplier': 1.5
                }
            },
            {
                'name': 'Catastrophic Scenario',
                'description': 'Extreme scenario with both frequency and severity increases',
                'modifications': {
                    'frequency_multiplier': 2.5,
                    'severity_multiplier': 2.0
                }
            },
            {
                'name': 'Low Frequency High Severity',
                'description': 'Rare but severe events scenario',
                'modifications': {
                    'frequency_multiplier': 0.5,
                    'severity_multiplier': 3.0
                }
            },
            {
                'name': 'Mild Stress Test',
                'description': 'Conservative stress test with minor increases',
                'modifications': {
                    'frequency_multiplier': 1.2,
                    'severity_multiplier': 1.1
                }
            },
            {
                'name': 'Economic Downturn',
                'description': 'Scenario modeling increased cyber risk during economic stress',
                'modifications': {
                    'frequency_multiplier': 1.3,
                    'severity_multiplier': 1.4,
                    'custom_modifications': {
                        'economic_factor': 1.5,
                        'business_continuity_impact': 1.2
                    }
                }
            }
        ]
        
        return jsonify({
            'templates': templates,
            'modification_types': {
                'frequency_multiplier': 'Multiplies the frequency distribution parameters',
                'severity_multiplier': 'Multiplies the severity distribution parameters',
                'frequency_additive': 'Adds to the frequency distribution parameters',
                'severity_additive': 'Adds to the severity distribution parameters',
                'frequency_param_modifications': 'Specific parameter modifications for frequency',
                'severity_param_modifications': 'Specific parameter modifications for severity',
                'custom_modifications': 'Custom scenario-specific modifications'
            }
        }), 200
        
    except Exception as e:
        logger.error("Failed to get scenario templates", error=str(e))
        return jsonify({'error': 'Failed to retrieve scenario templates'}), 500


@scenarios_bp.route('/compare', methods=['POST'])
@jwt_required()
def compare_scenarios():
    """
    Compare risk metrics between multiple scenarios.
    
    Expected JSON payload:
    {
        "scenario_ids": ["uuid1", "uuid2", "uuid3"],
        "metrics": ["expected_loss", "var_99", "tvar_99"]  // optional
    }
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Validate request data
        json_data = request.get_json()
        if not json_data or 'scenario_ids' not in json_data:
            return jsonify({'error': 'Scenario IDs are required'}), 400
        
        scenario_ids = json_data['scenario_ids']
        if not isinstance(scenario_ids, list) or len(scenario_ids) < 2:
            return jsonify({'error': 'At least 2 scenario IDs are required for comparison'}), 400
        
        if len(scenario_ids) > 10:
            return jsonify({'error': 'Maximum 10 scenarios can be compared at once'}), 400
        
        # Get scenarios
        scenarios = Scenario.query.filter(
            Scenario.id.in_(scenario_ids),
            Scenario.user_id == current_user_id
        ).all()
        
        if len(scenarios) != len(scenario_ids):
            return jsonify({'error': 'One or more scenarios not found'}), 404
        
        # Get requested metrics (default to common ones)
        requested_metrics = json_data.get('metrics', [
            'expected_loss', 'var_95', 'var_99', 'tvar_95', 'tvar_99'
        ])
        
        # Get simulation results for each scenario
        comparison_data = []
        
        for scenario in scenarios:
            # Get the most recent simulation for this scenario
            recent_simulation = scenario.simulation_runs.filter_by(status='completed').order_by(
                scenario.simulation_runs.property.mapper.class_.completed_at.desc()
            ).first()
            
            scenario_data = {
                'scenario': scenario.to_dict(),
                'has_results': recent_simulation is not None
            }
            
            if recent_simulation and recent_simulation.results:
                results = recent_simulation.results
                metrics_data = {}
                
                for metric in requested_metrics:
                    if hasattr(results, metric):
                        metrics_data[metric] = getattr(results, metric)
                
                scenario_data['results'] = metrics_data
                scenario_data['simulation_date'] = recent_simulation.completed_at.isoformat()
            
            comparison_data.append(scenario_data)
        
        # Calculate comparison statistics
        scenarios_with_results = [s for s in comparison_data if s['has_results']]
        
        if len(scenarios_with_results) < 2:
            return jsonify({
                'comparison': comparison_data,
                'summary': {
                    'scenarios_compared': len(scenarios_with_results),
                    'message': 'Insufficient simulation results for meaningful comparison'
                }
            }), 200
        
        # Find best and worst performers for each metric
        comparison_summary = {}
        
        for metric in requested_metrics:
            metric_values = []
            for scenario_data in scenarios_with_results:
                if 'results' in scenario_data and metric in scenario_data['results']:
                    metric_values.append({
                        'scenario_name': scenario_data['scenario']['name'],
                        'value': scenario_data['results'][metric]
                    })
            
            if metric_values:
                sorted_values = sorted(metric_values, key=lambda x: x['value'])
                comparison_summary[metric] = {
                    'lowest': sorted_values[0],
                    'highest': sorted_values[-1],
                    'range': sorted_values[-1]['value'] - sorted_values[0]['value'] if len(sorted_values) > 1 else 0
                }
        
        return jsonify({
            'comparison': comparison_data,
            'summary': {
                'scenarios_compared': len(scenarios_with_results),
                'metrics_analyzed': list(comparison_summary.keys()),
                'metric_comparisons': comparison_summary
            }
        }), 200
        
    except Exception as e:
        logger.error("Failed to compare scenarios", error=str(e))
        return jsonify({'error': 'Failed to compare scenarios'}), 500 