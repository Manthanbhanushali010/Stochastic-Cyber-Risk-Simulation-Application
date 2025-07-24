"""
API Routes Registration with Flask-RESTX Namespaces
This module registers all API endpoints using Flask-RESTX namespaces
for comprehensive Swagger documentation and request/response validation.
"""

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from datetime import datetime, timedelta
import json

from app.api_schemas import create_response, create_error_response, create_validation_error_response


def register_namespaces(api, app):
    """
    Register all API namespaces with the Flask-RESTX API instance
    
    Args:
        api: Flask-RESTX API instance
        app: Flask application instance
    """
    
    # Get API models from app config
    models = app.config['API_MODELS']
    
    # Create namespaces
    auth_ns = create_auth_namespace(api, models)
    simulation_ns = create_simulation_namespace(api, models)
    portfolio_ns = create_portfolio_namespace(api, models)
    scenarios_ns = create_scenarios_namespace(api, models)
    system_ns = create_system_namespace(api, models)
    
    # Register namespaces
    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(simulation_ns, path='/api/simulation')
    api.add_namespace(portfolio_ns, path='/api/portfolio')
    api.add_namespace(scenarios_ns, path='/api/scenarios')
    api.add_namespace(system_ns, path='/api/system')


def create_auth_namespace(api, models):
    """Create authentication namespace with endpoints"""
    
    ns = Namespace('Authentication', 
                   description='User authentication and account management operations',
                   path='/auth')
    
    @ns.route('/register')
    class RegisterResource(Resource):
        @ns.doc('register_user',
                description='Register a new user account with email and password')
        @ns.expect(models['register_model'], validate=True)
        @ns.response(201, 'User registered successfully', models['auth_response_model'])
        @ns.response(400, 'Validation error', models['validation_error_model'])
        @ns.response(409, 'User already exists', models['error_model'])
        def post(self):
            """Register a new user account"""
            try:
                from app.blueprints.auth import register_user
                return register_user()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/login')
    class LoginResource(Resource):
        @ns.doc('login_user',
                description='Authenticate user and receive access tokens')
        @ns.expect(models['login_model'], validate=True)
        @ns.response(200, 'Login successful', models['auth_response_model'])
        @ns.response(400, 'Invalid credentials', models['error_model'])
        @ns.response(401, 'Authentication failed', models['error_model'])
        def post(self):
            """Authenticate user and return JWT tokens"""
            try:
                from app.blueprints.auth import login_user
                return login_user()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/refresh')
    class RefreshTokenResource(Resource):
        @ns.doc('refresh_token',
                description='Refresh JWT access token using refresh token',
                security='Bearer')
        @ns.response(200, 'Token refreshed successfully', models['auth_response_model'])
        @ns.response(401, 'Invalid refresh token', models['error_model'])
        @jwt_required(refresh=True)
        def post(self):
            """Refresh JWT access token"""
            try:
                from app.blueprints.auth import refresh_token
                return refresh_token()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/logout')
    class LogoutResource(Resource):
        @ns.doc('logout_user',
                description='Logout user and invalidate tokens',
                security='Bearer')
        @ns.response(200, 'Logout successful', models['success_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def post(self):
            """Logout user and invalidate JWT tokens"""
            try:
                from app.blueprints.auth import logout_user
                return logout_user()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/profile')
    class ProfileResource(Resource):
        @ns.doc('get_user_profile',
                description='Get current user profile information',
                security='Bearer')
        @ns.response(200, 'Profile retrieved successfully', models['auth_response_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def get(self):
            """Get current user profile"""
            try:
                from app.blueprints.auth import get_user_profile
                return get_user_profile()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('update_user_profile',
                description='Update current user profile information',
                security='Bearer')
        @ns.expect(models['register_model'], validate=False)
        @ns.response(200, 'Profile updated successfully', models['success_model'])
        @ns.response(400, 'Validation error', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def put(self):
            """Update current user profile"""
            try:
                from app.blueprints.auth import update_user_profile
                return update_user_profile()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/change-password')
    class ChangePasswordResource(Resource):
        @ns.doc('change_password',
                description='Change user password',
                security='Bearer')
        @ns.expect(models['change_password_model'], validate=True)
        @ns.response(200, 'Password changed successfully', models['success_model'])
        @ns.response(400, 'Invalid current password', models['error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def post(self):
            """Change user password"""
            try:
                from app.blueprints.auth import change_password
                return change_password()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    return ns


def create_simulation_namespace(api, models):
    """Create simulation namespace with endpoints"""
    
    ns = Namespace('Simulation', 
                   description='Monte Carlo simulation operations and management',
                   path='/simulation')
    
    @ns.route('/run')
    class RunSimulationResource(Resource):
        @ns.doc('run_simulation',
                description='Start a new Monte Carlo simulation with specified parameters',
                security='Bearer')
        @ns.expect(models['simulation_parameters_model'], validate=True)
        @ns.response(202, 'Simulation started successfully', models['simulation_run_model'])
        @ns.response(400, 'Invalid simulation parameters', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(422, 'Business logic error', models['error_model'])
        @jwt_required()
        def post(self):
            """Start a new Monte Carlo simulation"""
            try:
                from app.blueprints.simulation import run_simulation
                return run_simulation()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/list')
    class ListSimulationsResource(Resource):
        @ns.doc('list_simulations',
                description='Get list of user simulations with optional filtering and pagination',
                security='Bearer')
        @ns.param('page', 'Page number', type='integer', default=1)
        @ns.param('per_page', 'Items per page', type='integer', default=10)
        @ns.param('status', 'Filter by status', type='string', enum=['running', 'completed', 'failed', 'cancelled'])
        @ns.response(200, 'Simulations retrieved successfully', 
                    api.model('SimulationList', {
                        'simulations': fields.List(fields.Nested(models['simulation_run_model'])),
                        'pagination': fields.Nested(models['pagination_model'])
                    }))
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def get(self):
            """Get list of user simulations"""
            try:
                from app.blueprints.simulation import list_simulations
                return list_simulations()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/<string:simulation_id>')
    class SimulationResource(Resource):
        @ns.doc('get_simulation',
                description='Get simulation details by ID',
                security='Bearer')
        @ns.response(200, 'Simulation retrieved successfully', models['simulation_run_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Simulation not found', models['error_model'])
        @jwt_required()
        def get(self, simulation_id):
            """Get simulation details by ID"""
            try:
                from app.blueprints.simulation import get_simulation
                return get_simulation(simulation_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('delete_simulation',
                description='Delete simulation by ID',
                security='Bearer')
        @ns.response(200, 'Simulation deleted successfully', models['success_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Simulation not found', models['error_model'])
        @jwt_required()
        def delete(self, simulation_id):
            """Delete simulation by ID"""
            try:
                from app.blueprints.simulation import delete_simulation
                return delete_simulation(simulation_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/<string:simulation_id>/results')
    class SimulationResultsResource(Resource):
        @ns.doc('get_simulation_results',
                description='Get detailed simulation results including risk metrics and charts',
                security='Bearer')
        @ns.response(200, 'Results retrieved successfully', models['simulation_result_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Simulation not found', models['error_model'])
        @ns.response(422, 'Simulation not completed', models['error_model'])
        @jwt_required()
        def get(self, simulation_id):
            """Get detailed simulation results"""
            try:
                from app.blueprints.simulation import get_simulation_results
                return get_simulation_results(simulation_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/<string:simulation_id>/stop')
    class StopSimulationResource(Resource):
        @ns.doc('stop_simulation',
                description='Stop a running simulation',
                security='Bearer')
        @ns.response(200, 'Simulation stopped successfully', models['success_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Simulation not found', models['error_model'])
        @ns.response(422, 'Simulation cannot be stopped', models['error_model'])
        @jwt_required()
        def post(self, simulation_id):
            """Stop a running simulation"""
            try:
                from app.blueprints.simulation import stop_simulation
                return stop_simulation(simulation_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/distributions')
    class AvailableDistributionsResource(Resource):
        @ns.doc('get_available_distributions',
                description='Get list of available probability distributions with parameters')
        @ns.response(200, 'Distributions retrieved successfully',
                    api.model('DistributionsList', {
                        'distributions': fields.List(fields.Nested(models['distribution_model']))
                    }))
        def get(self):
            """Get available probability distributions"""
            try:
                from app.blueprints.simulation import get_available_distributions
                return get_available_distributions()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    return ns


def create_portfolio_namespace(api, models):
    """Create portfolio namespace with endpoints"""
    
    ns = Namespace('Portfolio', 
                   description='Portfolio and policy management operations',
                   path='/portfolio')
    
    @ns.route('/')
    class PortfolioListResource(Resource):
        @ns.doc('list_portfolios',
                description='Get list of user portfolios with pagination',
                security='Bearer')
        @ns.param('page', 'Page number', type='integer', default=1)
        @ns.param('per_page', 'Items per page', type='integer', default=10)
        @ns.response(200, 'Portfolios retrieved successfully',
                    api.model('PortfolioList', {
                        'portfolios': fields.List(fields.Nested(models['portfolio_model'])),
                        'pagination': fields.Nested(models['pagination_model'])
                    }))
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def get(self):
            """Get list of user portfolios"""
            try:
                from app.blueprints.portfolio import list_portfolios
                return list_portfolios()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('create_portfolio',
                description='Create a new portfolio',
                security='Bearer')
        @ns.expect(models['portfolio_model'], validate=True)
        @ns.response(201, 'Portfolio created successfully', models['portfolio_model'])
        @ns.response(400, 'Validation error', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def post(self):
            """Create a new portfolio"""
            try:
                from app.blueprints.portfolio import create_portfolio
                return create_portfolio()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/<string:portfolio_id>')
    class PortfolioResource(Resource):
        @ns.doc('get_portfolio',
                description='Get portfolio details by ID',
                security='Bearer')
        @ns.response(200, 'Portfolio retrieved successfully', models['portfolio_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Portfolio not found', models['error_model'])
        @jwt_required()
        def get(self, portfolio_id):
            """Get portfolio details by ID"""
            try:
                from app.blueprints.portfolio import get_portfolio
                return get_portfolio(portfolio_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('update_portfolio',
                description='Update portfolio details',
                security='Bearer')
        @ns.expect(models['portfolio_model'], validate=False)
        @ns.response(200, 'Portfolio updated successfully', models['portfolio_model'])
        @ns.response(400, 'Validation error', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Portfolio not found', models['error_model'])
        @jwt_required()
        def put(self, portfolio_id):
            """Update portfolio details"""
            try:
                from app.blueprints.portfolio import update_portfolio
                return update_portfolio(portfolio_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('delete_portfolio',
                description='Delete portfolio by ID',
                security='Bearer')
        @ns.response(200, 'Portfolio deleted successfully', models['success_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Portfolio not found', models['error_model'])
        @jwt_required()
        def delete(self, portfolio_id):
            """Delete portfolio by ID"""
            try:
                from app.blueprints.portfolio import delete_portfolio
                return delete_portfolio(portfolio_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/<string:portfolio_id>/policies')
    class PortfolioPoliciesResource(Resource):
        @ns.doc('get_portfolio_policies',
                description='Get all policies in a portfolio',
                security='Bearer')
        @ns.response(200, 'Policies retrieved successfully',
                    api.model('PoliciesList', {
                        'policies': fields.List(fields.Nested(models['policy_model']))
                    }))
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Portfolio not found', models['error_model'])
        @jwt_required()
        def get(self, portfolio_id):
            """Get all policies in a portfolio"""
            try:
                from app.blueprints.portfolio import get_portfolio_policies
                return get_portfolio_policies(portfolio_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('create_policy',
                description='Add a new policy to portfolio',
                security='Bearer')
        @ns.expect(models['policy_model'], validate=True)
        @ns.response(201, 'Policy created successfully', models['policy_model'])
        @ns.response(400, 'Validation error', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Portfolio not found', models['error_model'])
        @jwt_required()
        def post(self, portfolio_id):
            """Add a new policy to portfolio"""
            try:
                from app.blueprints.portfolio import create_policy
                return create_policy(portfolio_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/<string:portfolio_id>/summary')
    class PortfolioSummaryResource(Resource):
        @ns.doc('get_portfolio_summary',
                description='Get portfolio summary with aggregated metrics',
                security='Bearer')
        @ns.response(200, 'Summary retrieved successfully', models['portfolio_summary_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Portfolio not found', models['error_model'])
        @jwt_required()
        def get(self, portfolio_id):
            """Get portfolio summary with aggregated metrics"""
            try:
                from app.blueprints.portfolio import get_portfolio_summary
                return get_portfolio_summary(portfolio_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    return ns


def create_scenarios_namespace(api, models):
    """Create scenarios namespace with endpoints"""
    
    ns = Namespace('Scenarios', 
                   description='Risk scenario creation, management, and analysis',
                   path='/scenarios')
    
    @ns.route('/')
    class ScenarioListResource(Resource):
        @ns.doc('list_scenarios',
                description='Get list of risk scenarios with filtering options',
                security='Bearer')
        @ns.param('page', 'Page number', type='integer', default=1)
        @ns.param('per_page', 'Items per page', type='integer', default=10)
        @ns.param('threat_level', 'Filter by threat level', type='string', enum=['low', 'medium', 'high'])
        @ns.param('is_active', 'Filter by active status', type='boolean')
        @ns.response(200, 'Scenarios retrieved successfully',
                    api.model('ScenarioList', {
                        'scenarios': fields.List(fields.Nested(models['scenario_model'])),
                        'pagination': fields.Nested(models['pagination_model'])
                    }))
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def get(self):
            """Get list of risk scenarios"""
            try:
                from app.blueprints.scenarios import list_scenarios
                return list_scenarios()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('create_scenario',
                description='Create a new risk scenario',
                security='Bearer')
        @ns.expect(models['scenario_model'], validate=True)
        @ns.response(201, 'Scenario created successfully', models['scenario_model'])
        @ns.response(400, 'Validation error', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def post(self):
            """Create a new risk scenario"""
            try:
                from app.blueprints.scenarios import create_scenario
                return create_scenario()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/<string:scenario_id>')
    class ScenarioResource(Resource):
        @ns.doc('get_scenario',
                description='Get scenario details by ID',
                security='Bearer')
        @ns.response(200, 'Scenario retrieved successfully', models['scenario_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Scenario not found', models['error_model'])
        @jwt_required()
        def get(self, scenario_id):
            """Get scenario details by ID"""
            try:
                from app.blueprints.scenarios import get_scenario
                return get_scenario(scenario_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('update_scenario',
                description='Update scenario details',
                security='Bearer')
        @ns.expect(models['scenario_model'], validate=False)
        @ns.response(200, 'Scenario updated successfully', models['scenario_model'])
        @ns.response(400, 'Validation error', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Scenario not found', models['error_model'])
        @jwt_required()
        def put(self, scenario_id):
            """Update scenario details"""
            try:
                from app.blueprints.scenarios import update_scenario
                return update_scenario(scenario_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
        
        @ns.doc('delete_scenario',
                description='Delete scenario by ID',
                security='Bearer')
        @ns.response(200, 'Scenario deleted successfully', models['success_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @ns.response(404, 'Scenario not found', models['error_model'])
        @jwt_required()
        def delete(self, scenario_id):
            """Delete scenario by ID"""
            try:
                from app.blueprints.scenarios import delete_scenario
                return delete_scenario(scenario_id)
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/compare')
    class CompareScenarios(Resource):
        @ns.doc('compare_scenarios',
                description='Compare multiple scenarios and generate analysis',
                security='Bearer')
        @ns.expect(api.model('ScenarioCompareRequest', {
            'scenario_ids': fields.List(fields.String, required=True, description='List of scenario IDs to compare')
        }), validate=True)
        @ns.response(200, 'Comparison completed successfully', models['scenario_comparison_model'])
        @ns.response(400, 'Invalid scenario IDs', models['validation_error_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def post(self):
            """Compare multiple scenarios"""
            try:
                from app.blueprints.scenarios import compare_scenarios
                return compare_scenarios()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    return ns


def create_system_namespace(api, models):
    """Create system namespace with endpoints"""
    
    ns = Namespace('System', 
                   description='System health, information, and administration endpoints',
                   path='/system')
    
    @ns.route('/health')
    class HealthCheckResource(Resource):
        @ns.doc('health_check',
                description='Check system health and service status')
        @ns.response(200, 'System is healthy', models['health_check_model'])
        @ns.response(503, 'System is unhealthy', models['health_check_model'])
        def get(self):
            """Check system health"""
            try:
                from app.blueprints.api import health_check
                return health_check()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/info')
    class SystemInfoResource(Resource):
        @ns.doc('system_info',
                description='Get system information and configuration')
        @ns.response(200, 'System info retrieved successfully', models['system_info_model'])
        def get(self):
            """Get system information"""
            try:
                from app.blueprints.api import system_info
                return system_info()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    @ns.route('/stats')
    class SystemStatsResource(Resource):
        @ns.doc('system_stats',
                description='Get system usage statistics',
                security='Bearer')
        @ns.response(200, 'Stats retrieved successfully', models['stats_model'])
        @ns.response(401, 'Authentication required', models['error_model'])
        @jwt_required()
        def get(self):
            """Get system usage statistics"""
            try:
                from app.blueprints.api import system_stats
                return system_stats()
            except Exception as e:
                return create_error_response(str(e), status_code=500)
    
    return ns 