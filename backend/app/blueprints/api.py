"""
Main API blueprint for general endpoints, health checks, and system information.

This module provides general API endpoints that don't belong to specific
functional areas like authentication or simulation management.
"""

from datetime import datetime, timezone
from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import psutil
import os
import structlog

from app import db
from app.models import User, SimulationRun, Portfolio, Scenario, SystemConfiguration
from app.simulation import DistributionFactory

logger = structlog.get_logger(__name__)

# Create the main API blueprint
api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint.
    
    Returns system status and basic information.
    """
    try:
        # Check database connectivity
        db_status = 'healthy'
        try:
            db.session.execute('SELECT 1')
            db.session.commit()
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        # Get system information
        system_info = {
            'status': 'healthy' if db_status == 'healthy' else 'degraded',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'database': db_status,
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        }
        
        return jsonify(system_info), 200 if system_info['status'] == 'healthy' else 503
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e)
        }), 503


@api_bp.route('/status', methods=['GET'])
@jwt_required()
def system_status():
    """
    Detailed system status for authenticated users.
    
    Requires authentication and returns detailed system metrics.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only allow admin users to view detailed status
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # System metrics
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Database statistics
        total_users = User.query.count()
        total_simulations = SimulationRun.query.count()
        total_portfolios = Portfolio.query.count()
        total_scenarios = Scenario.query.count()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        recent_simulations = SimulationRun.query.filter(SimulationRun.created_at >= yesterday).count()
        recent_users = User.query.filter(User.created_at >= yesterday).count()
        
        # Running simulations
        running_simulations = SimulationRun.query.filter_by(status='running').count()
        pending_simulations = SimulationRun.query.filter_by(status='pending').count()
        
        status_info = {
            'system': {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'uptime_seconds': int((datetime.now(timezone.utc) - datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)).total_seconds()),
                'cpu_usage_percent': cpu_percent,
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'usage_percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 2)
                }
            },
            'database': {
                'total_users': total_users,
                'total_simulations': total_simulations,
                'total_portfolios': total_portfolios,
                'total_scenarios': total_scenarios,
                'running_simulations': running_simulations,
                'pending_simulations': pending_simulations
            },
            'activity_24h': {
                'new_simulations': recent_simulations,
                'new_users': recent_users
            },
            'application': {
                'version': '1.0.0',
                'environment': os.environ.get('FLASK_ENV', 'development'),
                'debug_mode': current_app.debug,
                'available_distributions': DistributionFactory.get_available_distributions()
            }
        }
        
        return jsonify(status_info), 200
        
    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        return jsonify({'error': 'Failed to retrieve system status'}), 500


@api_bp.route('/info', methods=['GET'])
def api_info():
    """
    General API information endpoint.
    
    Returns API version, available endpoints, and documentation links.
    """
    try:
        api_info = {
            'name': 'Cyber Risk Simulation API',
            'version': '1.0.0',
            'description': 'Production-ready API for stochastic cyber risk event simulation and impact analysis',
            'documentation': '/docs',  # Future Swagger/OpenAPI docs
            'endpoints': {
                'authentication': {
                    'base_path': '/api/auth',
                    'endpoints': [
                        'POST /register - User registration',
                        'POST /login - User login',
                        'POST /refresh - Token refresh',
                        'POST /logout - User logout',
                        'GET /profile - Get user profile',
                        'PUT /profile - Update user profile',
                        'POST /change-password - Change password',
                        'GET /verify - Verify token'
                    ]
                },
                'simulation': {
                    'base_path': '/api/simulation',
                    'endpoints': [
                        'POST /run - Start new simulation',
                        'GET /list - List user simulations',
                        'GET /<id> - Get simulation details',
                        'GET /<id>/results - Get simulation results',
                        'POST /<id>/stop - Stop running simulation',
                        'DELETE /<id> - Delete simulation',
                        'GET /distributions - Get available distributions'
                    ]
                },
                'portfolio': {
                    'base_path': '/api/portfolio',
                    'endpoints': [
                        'POST / - Create portfolio',
                        'GET / - List portfolios',
                        'GET /<id> - Get portfolio details',
                        'PUT /<id> - Update portfolio',
                        'DELETE /<id> - Delete portfolio',
                        'POST /<id>/policies - Add policy to portfolio',
                        'PUT /<id>/policies/<policy_id> - Update policy',
                        'DELETE /<id>/policies/<policy_id> - Delete policy',
                        'GET /<id>/summary - Get portfolio summary'
                    ]
                },
                'scenarios': {
                    'base_path': '/api/scenarios',
                    'endpoints': [
                        'POST / - Create scenario',
                        'GET / - List scenarios',
                        'GET /<id> - Get scenario details',
                        'PUT /<id> - Update scenario',
                        'DELETE /<id> - Delete scenario',
                        'POST /<id>/activate - Activate scenario',
                        'POST /<id>/deactivate - Deactivate scenario',
                        'POST /<id>/duplicate - Duplicate scenario',
                        'GET /templates - Get scenario templates',
                        'POST /compare - Compare scenarios'
                    ]
                },
                'general': {
                    'base_path': '/api',
                    'endpoints': [
                        'GET /health - Health check',
                        'GET /status - System status (admin only)',
                        'GET /info - API information',
                        'GET /config - System configuration (admin only)'
                    ]
                }
            },
            'features': [
                'Monte Carlo simulation with multiple distributions',
                'Insurance portfolio modeling',
                'Financial impact calculations with policy terms',
                'Risk metrics (VaR, TVaR, Expected Loss)',
                'Scenario analysis and comparison',
                'Real-time simulation progress updates',
                'Comprehensive authentication and authorization',
                'RESTful API with JSON responses',
                'WebSocket support for real-time updates'
            ],
            'supported_distributions': DistributionFactory.get_available_distributions(),
            'contact': {
                'documentation': '/docs',
                'support': 'GitHub Issues',
                'repository': 'https://github.com/your-org/cyber-risk-simulation'
            }
        }
        
        return jsonify(api_info), 200
        
    except Exception as e:
        logger.error("Failed to get API info", error=str(e))
        return jsonify({'error': 'Failed to retrieve API information'}), 500


@api_bp.route('/config', methods=['GET'])
@jwt_required()
def get_system_config():
    """
    Get system configuration settings.
    
    Admin-only endpoint for retrieving system configuration.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only allow admin users to view system configuration
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get all system configurations
        configs = SystemConfiguration.query.all()
        
        config_dict = {}
        for config in configs:
            config_dict[config.key] = {
                'value': config.value,
                'description': config.description,
                'updated_at': config.updated_at.isoformat()
            }
        
        return jsonify({
            'configurations': config_dict,
            'total_configs': len(configs)
        }), 200
        
    except Exception as e:
        logger.error("Failed to get system config", error=str(e))
        return jsonify({'error': 'Failed to retrieve system configuration'}), 500


@api_bp.route('/config/<config_key>', methods=['PUT'])
@jwt_required()
def update_system_config(config_key: str):
    """
    Update a system configuration setting.
    
    Admin-only endpoint for updating system configuration.
    
    Expected JSON payload:
    {
        "value": "new_value",
        "description": "Optional description"
    }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Only allow admin users to update system configuration
        if user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Validate request data
        json_data = request.get_json()
        if not json_data or 'value' not in json_data:
            return jsonify({'error': 'Configuration value is required'}), 400
        
        # Get or create configuration
        config = SystemConfiguration.query.filter_by(key=config_key).first()
        
        if not config:
            config = SystemConfiguration(key=config_key)
            db.session.add(config)
        
        # Update configuration
        config.value = json_data['value']
        if 'description' in json_data:
            config.description = json_data['description']
        config.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        logger.info("System configuration updated", 
                   config_key=config_key, 
                   admin_user_id=current_user_id)
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'configuration': config.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to update system config", error=str(e))
        return jsonify({'error': 'Failed to update system configuration'}), 500


@api_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    Get statistics for the current user.
    
    Returns user-specific statistics about their simulations and portfolios.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # User statistics
        total_simulations = user.simulation_runs.count()
        completed_simulations = user.simulation_runs.filter_by(status='completed').count()
        running_simulations = user.simulation_runs.filter_by(status='running').count()
        failed_simulations = user.simulation_runs.filter_by(status='failed').count()
        
        total_portfolios = user.portfolios.count()
        total_scenarios = user.scenarios.count()
        active_scenarios = user.scenarios.filter_by(is_active=True).count()
        
        # Recent activity (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_simulations = user.simulation_runs.filter(
            SimulationRun.created_at >= week_ago
        ).count()
        
        # Most used distributions
        simulation_runs = user.simulation_runs.all()
        freq_distributions = {}
        sev_distributions = {}
        
        for sim in simulation_runs:
            if sim.event_parameters:
                freq_dist = sim.event_parameters.get('frequency_distribution')
                sev_dist = sim.event_parameters.get('severity_distribution')
                
                if freq_dist:
                    freq_distributions[freq_dist] = freq_distributions.get(freq_dist, 0) + 1
                if sev_dist:
                    sev_distributions[sev_dist] = sev_distributions.get(sev_dist, 0) + 1
        
        stats = {
            'user_info': {
                'user_id': str(user.id),
                'username': user.username,
                'member_since': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'simulation_stats': {
                'total': total_simulations,
                'completed': completed_simulations,
                'running': running_simulations,
                'failed': failed_simulations,
                'success_rate': round((completed_simulations / total_simulations * 100), 2) if total_simulations > 0 else 0,
                'recent_week': recent_simulations
            },
            'portfolio_stats': {
                'total_portfolios': total_portfolios,
                'total_policies': sum(portfolio.policies.count() for portfolio in user.portfolios)
            },
            'scenario_stats': {
                'total_scenarios': total_scenarios,
                'active_scenarios': active_scenarios
            },
            'preferences': {
                'most_used_frequency_distributions': dict(sorted(freq_distributions.items(), key=lambda x: x[1], reverse=True)[:5]),
                'most_used_severity_distributions': dict(sorted(sev_distributions.items(), key=lambda x: x[1], reverse=True)[:5])
            }
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error("Failed to get user stats", error=str(e))
        return jsonify({'error': 'Failed to retrieve user statistics'}), 500


# Error handlers for the API blueprint
@api_bp.errorhandler(404)
def handle_not_found(e):
    """Handle 404 errors for API endpoints."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist',
        'status_code': 404
    }), 404


@api_bp.errorhandler(405)
def handle_method_not_allowed(e):
    """Handle 405 errors for API endpoints."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint',
        'status_code': 405
    }), 405


@api_bp.errorhandler(500)
def handle_internal_error(e):
    """Handle 500 errors for API endpoints."""
    logger.error("Internal server error in API", error=str(e))
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500 