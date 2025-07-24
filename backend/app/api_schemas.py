"""
API Schemas and Models for Swagger Documentation
This module defines all API schemas used across the application for
request/response validation and Swagger documentation generation.
"""

from flask_restx import fields
from datetime import datetime

# Common field types
def create_api_models(api):
    """Create all API models for Swagger documentation"""
    
    # Authentication Models
    login_model = api.model('LoginRequest', {
        'email': fields.String(required=True, description='User email address', example='user@example.com'),
        'password': fields.String(required=True, description='User password', example='password123')
    })
    
    register_model = api.model('RegisterRequest', {
        'email': fields.String(required=True, description='User email address', example='user@example.com'),
        'username': fields.String(required=True, description='Unique username', example='johndoe'),
        'password': fields.String(required=True, description='User password (min 6 characters)', example='password123'),
        'first_name': fields.String(description='First name', example='John'),
        'last_name': fields.String(description='Last name', example='Doe')
    })
    
    auth_response_model = api.model('AuthResponse', {
        'access_token': fields.String(description='JWT access token'),
        'refresh_token': fields.String(description='JWT refresh token'),
        'user': fields.Nested(api.model('UserInfo', {
            'id': fields.String(description='User ID'),
            'email': fields.String(description='User email'),
            'username': fields.String(description='Username'),
            'first_name': fields.String(description='First name'),
            'last_name': fields.String(description='Last name'),
            'created_at': fields.DateTime(description='Account creation date')
        }))
    })
    
    change_password_model = api.model('ChangePasswordRequest', {
        'current_password': fields.String(required=True, description='Current password'),
        'new_password': fields.String(required=True, description='New password (min 6 characters)')
    })
    
    # Distribution Models
    distribution_param_model = api.model('DistributionParameters', {
        'lambda': fields.Float(description='Lambda parameter for Poisson distribution'),
        'mean': fields.Float(description='Mean parameter for Log-Normal distribution'),
        'std': fields.Float(description='Standard deviation for Log-Normal distribution'),
        'scale': fields.Float(description='Scale parameter for Pareto/Gamma distributions'),
        'shape': fields.Float(description='Shape parameter for Pareto/Gamma distributions'),
        'rate': fields.Float(description='Rate parameter for Exponential distribution'),
        'n': fields.Integer(description='N parameter for Negative Binomial distribution'),
        'p': fields.Float(description='P parameter for Negative Binomial distribution')
    })
    
    distribution_model = api.model('Distribution', {
        'type': fields.String(required=True, description='Distribution type', 
                            enum=['poisson', 'lognormal', 'pareto', 'gamma', 'exponential', 'weibull', 'negative_binomial', 'binomial']),
        'parameters': fields.Nested(distribution_param_model, required=True, description='Distribution parameters')
    })
    
    # Portfolio and Policy Models
    policy_model = api.model('Policy', {
        'id': fields.String(description='Policy ID'),
        'name': fields.String(required=True, description='Policy name', example='Cyber Liability Policy'),
        'limit': fields.Float(required=True, description='Policy limit amount', example=5000000),
        'deductible': fields.Float(description='Deductible amount', example=50000),
        'premium': fields.Float(description='Annual premium', example=100000),
        'coverage_type': fields.String(description='Type of coverage', example='cyber',
                                     enum=['cyber', 'data_breach', 'errors_omissions', 'general_liability', 'other']),
        'inception_date': fields.DateTime(description='Policy start date'),
        'expiry_date': fields.DateTime(description='Policy end date'),
        'coinsurance': fields.Float(description='Coinsurance rate (0.0-1.0)', example=0.2),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'updated_at': fields.DateTime(description='Last update timestamp')
    })
    
    portfolio_model = api.model('Portfolio', {
        'id': fields.String(description='Portfolio ID'),
        'name': fields.String(required=True, description='Portfolio name', example='Tech Company Portfolio'),
        'description': fields.String(description='Portfolio description'),
        'total_value': fields.Float(required=True, description='Total portfolio value', example=10000000),
        'industry': fields.String(description='Industry sector', example='technology'),
        'policies': fields.List(fields.Nested(policy_model), description='Associated policies'),
        'policy_count': fields.Integer(description='Number of policies'),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'updated_at': fields.DateTime(description='Last update timestamp')
    })
    
    portfolio_summary_model = api.model('PortfolioSummary', {
        'total_premium': fields.Float(description='Total premium across all policies'),
        'total_coverage': fields.Float(description='Total coverage limit'),
        'average_deductible': fields.Float(description='Average deductible amount'),
        'policy_count': fields.Integer(description='Number of active policies'),
        'risk_score': fields.Float(description='Calculated risk score (0-10)')
    })
    
    # Simulation Models
    event_parameters_model = api.model('EventParameters', {
        'frequency_distribution': fields.Nested(distribution_model, required=True, description='Frequency distribution'),
        'severity_distribution': fields.Nested(distribution_model, required=True, description='Severity distribution')
    })
    
    simulation_parameters_model = api.model('SimulationParameters', {
        'name': fields.String(required=True, description='Simulation name', example='Q4 Cyber Risk Assessment'),
        'description': fields.String(description='Simulation description'),
        'iterations': fields.Integer(required=True, description='Number of Monte Carlo iterations', example=10000, min=1000, max=100000),
        'random_seed': fields.Integer(description='Random seed for reproducibility', example=42),
        'confidence_levels': fields.List(fields.Float, description='Confidence levels for VaR calculation', example=[90, 95, 99]),
        'event_parameters': fields.Nested(event_parameters_model, required=True, description='Event distribution parameters'),
        'portfolio': fields.Nested(api.model('SimulationPortfolio', {
            'total_value': fields.Float(required=True, description='Portfolio total value'),
            'policies': fields.List(fields.Nested(policy_model), description='Portfolio policies')
        }), required=True, description='Portfolio configuration')
    })
    
    risk_metrics_model = api.model('RiskMetrics', {
        'expected_loss': fields.Float(description='Expected annual loss'),
        'standard_deviation': fields.Float(description='Standard deviation of losses'),
        'var_90': fields.Float(description='Value at Risk at 90% confidence'),
        'var_95': fields.Float(description='Value at Risk at 95% confidence'),
        'var_99': fields.Float(description='Value at Risk at 99% confidence'),
        'tvar_90': fields.Float(description='Tail Value at Risk at 90% confidence'),
        'tvar_95': fields.Float(description='Tail Value at Risk at 95% confidence'),
        'tvar_99': fields.Float(description='Tail Value at Risk at 99% confidence'),
        'max_loss': fields.Float(description='Maximum simulated loss'),
        'min_loss': fields.Float(description='Minimum simulated loss'),
        'skewness': fields.Float(description='Distribution skewness'),
        'kurtosis': fields.Float(description='Distribution kurtosis')
    })
    
    histogram_data_model = api.model('HistogramData', {
        'bins': fields.List(fields.Float, description='Histogram bin edges'),
        'frequencies': fields.List(fields.Integer, description='Frequency counts for each bin'),
        'densities': fields.List(fields.Float, description='Probability densities for each bin')
    })
    
    exceedance_curve_model = api.model('ExceedanceCurve', {
        'loss_amounts': fields.List(fields.Float, description='Loss amounts'),
        'probabilities': fields.List(fields.Float, description='Exceedance probabilities')
    })
    
    simulation_result_model = api.model('SimulationResult', {
        'simulation_run_id': fields.String(description='Simulation run ID'),
        'status': fields.String(description='Simulation status', enum=['running', 'completed', 'failed', 'cancelled']),
        'progress': fields.Float(description='Completion progress (0-100)'),
        'iterations': fields.Integer(description='Number of iterations completed'),
        'runtime_seconds': fields.Float(description='Runtime in seconds'),
        'risk_metrics': fields.Nested(risk_metrics_model, description='Calculated risk metrics'),
        'histogram_data': fields.Nested(histogram_data_model, description='Loss distribution histogram'),
        'exceedance_curves': fields.Nested(exceedance_curve_model, description='Exceedance probability curves'),
        'parameters': fields.Nested(simulation_parameters_model, description='Original simulation parameters'),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'completed_at': fields.DateTime(description='Completion timestamp'),
        'random_seed': fields.Integer(description='Random seed used')
    })
    
    simulation_run_model = api.model('SimulationRun', {
        'id': fields.String(description='Simulation run ID'),
        'name': fields.String(description='Simulation name'),
        'description': fields.String(description='Simulation description'),
        'status': fields.String(description='Current status'),
        'progress': fields.Float(description='Progress percentage'),
        'user_id': fields.String(description='User who created the simulation'),
        'parameters': fields.Nested(simulation_parameters_model, description='Simulation parameters'),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'updated_at': fields.DateTime(description='Last update timestamp')
    })
    
    # Scenario Models
    scenario_model = api.model('Scenario', {
        'id': fields.String(description='Scenario ID'),
        'name': fields.String(required=True, description='Scenario name', example='Advanced Persistent Threat'),
        'description': fields.String(description='Scenario description'),
        'threat_level': fields.String(description='Threat level', enum=['low', 'medium', 'high'], example='high'),
        'frequency_distribution': fields.Nested(distribution_model, description='Frequency distribution'),
        'severity_distribution': fields.Nested(distribution_model, description='Severity distribution'),
        'industry_focus': fields.List(fields.String, description='Target industries'),
        'is_active': fields.Boolean(description='Whether scenario is active'),
        'is_template': fields.Boolean(description='Whether scenario is a template'),
        'created_by': fields.String(description='User who created the scenario'),
        'created_at': fields.DateTime(description='Creation timestamp'),
        'updated_at': fields.DateTime(description='Last update timestamp')
    })
    
    scenario_comparison_model = api.model('ScenarioComparison', {
        'scenarios': fields.List(fields.Nested(scenario_model), description='Compared scenarios'),
        'metrics_comparison': fields.Raw(description='Risk metrics comparison data'),
        'risk_profiles': fields.Raw(description='Risk profile comparison data'),
        'recommendations': fields.List(fields.String, description='Analysis recommendations')
    })
    
    # System Models
    system_info_model = api.model('SystemInfo', {
        'version': fields.String(description='Application version'),
        'environment': fields.String(description='Environment (dev/staging/prod)'),
        'database_status': fields.String(description='Database connection status'),
        'redis_status': fields.String(description='Redis connection status'),
        'features': fields.List(fields.String, description='Enabled features')
    })
    
    health_check_model = api.model('HealthCheck', {
        'status': fields.String(description='Overall health status', enum=['healthy', 'degraded', 'unhealthy']),
        'timestamp': fields.DateTime(description='Check timestamp'),
        'services': fields.Raw(description='Individual service statuses'),
        'uptime_seconds': fields.Float(description='Application uptime in seconds')
    })
    
    stats_model = api.model('SystemStats', {
        'total_users': fields.Integer(description='Total registered users'),
        'total_simulations': fields.Integer(description='Total simulations run'),
        'total_portfolios': fields.Integer(description='Total portfolios created'),
        'total_scenarios': fields.Integer(description='Total scenarios created'),
        'active_simulations': fields.Integer(description='Currently running simulations'),
        'average_simulation_time': fields.Float(description='Average simulation runtime (seconds)')
    })
    
    # Error Models
    error_model = api.model('Error', {
        'error': fields.String(description='Error type'),
        'message': fields.String(description='Error message'),
        'details': fields.Raw(description='Additional error details'),
        'timestamp': fields.DateTime(description='Error timestamp')
    })
    
    validation_error_model = api.model('ValidationError', {
        'error': fields.String(description='Error type', example='validation_error'),
        'message': fields.String(description='Error message'),
        'errors': fields.Raw(description='Field-specific validation errors'),
        'timestamp': fields.DateTime(description='Error timestamp')
    })
    
    # Success Models
    success_model = api.model('Success', {
        'success': fields.Boolean(description='Operation success status', example=True),
        'message': fields.String(description='Success message'),
        'data': fields.Raw(description='Response data'),
        'timestamp': fields.DateTime(description='Response timestamp')
    })
    
    # Pagination Models
    pagination_model = api.model('Pagination', {
        'page': fields.Integer(description='Current page number'),
        'per_page': fields.Integer(description='Items per page'),
        'total': fields.Integer(description='Total number of items'),
        'pages': fields.Integer(description='Total number of pages'),
        'has_prev': fields.Boolean(description='Has previous page'),
        'has_next': fields.Boolean(description='Has next page'),
        'prev_num': fields.Integer(description='Previous page number'),
        'next_num': fields.Integer(description='Next page number')
    })
    
    # Return all models as a dictionary for easy access
    return {
        # Auth models
        'login_model': login_model,
        'register_model': register_model,
        'auth_response_model': auth_response_model,
        'change_password_model': change_password_model,
        
        # Distribution models
        'distribution_model': distribution_model,
        'distribution_param_model': distribution_param_model,
        
        # Portfolio models
        'policy_model': policy_model,
        'portfolio_model': portfolio_model,
        'portfolio_summary_model': portfolio_summary_model,
        
        # Simulation models
        'simulation_parameters_model': simulation_parameters_model,
        'simulation_result_model': simulation_result_model,
        'simulation_run_model': simulation_run_model,
        'risk_metrics_model': risk_metrics_model,
        'histogram_data_model': histogram_data_model,
        'exceedance_curve_model': exceedance_curve_model,
        
        # Scenario models
        'scenario_model': scenario_model,
        'scenario_comparison_model': scenario_comparison_model,
        
        # System models
        'system_info_model': system_info_model,
        'health_check_model': health_check_model,
        'stats_model': stats_model,
        
        # Common models
        'error_model': error_model,
        'validation_error_model': validation_error_model,
        'success_model': success_model,
        'pagination_model': pagination_model
    }


# Common response decorators and functions for consistent API responses
def create_response(data=None, message=None, status_code=200):
    """Create a standardized API response"""
    return {
        'success': status_code < 400,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, status_code


def create_error_response(message, details=None, status_code=400):
    """Create a standardized error response"""
    return {
        'error': 'api_error',
        'message': message,
        'details': details,
        'timestamp': datetime.utcnow().isoformat()
    }, status_code


def create_validation_error_response(errors, message="Validation failed"):
    """Create a standardized validation error response"""
    return {
        'error': 'validation_error',
        'message': message,
        'errors': errors,
        'timestamp': datetime.utcnow().isoformat()
    }, 400 