"""
Flask Application Factory with Swagger Documentation
This module creates and configures the Flask application with all extensions,
including comprehensive API documentation using Flask-RESTX.
"""

import os
import structlog
from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_restx import Api
from werkzeug.exceptions import HTTPException

# Import configuration
from config import config
from app.api_schemas import create_api_models

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
socketio = SocketIO()

# Global API instance (will be initialized in create_app)
api = None

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def create_app(config_name=None):
    """
    Create and configure Flask application with Swagger documentation
    
    Args:
        config_name: Configuration environment ('development', 'testing', 'production', 'docker')
    
    Returns:
        Flask application instance with full API documentation
    """
    global api
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    try:
        app.config.from_object(config[config_name])
        logger.info("Configuration loaded", config=config_name)
    except KeyError:
        logger.error("Invalid configuration name", config=config_name)
        raise ValueError(f"Invalid configuration: {config_name}")
    
    # Initialize Flask-RESTX API with comprehensive documentation
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    }
    
    api = Api(
        app,
        version='1.0.0',
        title='Stochastic Cyber Risk Simulation API',
        description='''
        ## Advanced Monte Carlo Cyber Risk Simulation Platform

        This comprehensive API provides enterprise-grade cyber risk simulation capabilities using advanced statistical methods and Monte Carlo techniques.

        ### Key Features
        - **Monte Carlo Simulation Engine**: Run sophisticated risk simulations with multiple probability distributions
        - **Portfolio Management**: Manage insurance portfolios and policies with detailed coverage analysis
        - **Scenario Analysis**: Create, compare, and analyze different cyber threat scenarios
        - **Risk Metrics**: Calculate VaR, TVaR, Expected Loss, and other advanced risk metrics
        - **Real-time Updates**: WebSocket integration for live simulation progress tracking
        - **User Management**: Secure authentication and profile management
        - **Data Visualization**: Generate charts and export results for reporting

        ### Authentication
        Most endpoints require JWT authentication. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your-jwt-token>
        ```

        ### Error Handling
        The API uses standard HTTP status codes and returns consistent error responses:
        - `200-299`: Success responses
        - `400`: Bad Request (validation errors)
        - `401`: Unauthorized (authentication required)
        - `403`: Forbidden (insufficient permissions)
        - `404`: Not Found
        - `422`: Unprocessable Entity (business logic errors)
        - `500`: Internal Server Error

        ### Rate Limiting
        API requests are rate-limited to ensure fair usage and system stability.

        ### WebSocket Events
        Real-time updates are available via WebSocket connections for:
        - Simulation progress updates
        - System notifications
        - Result completion alerts

        ### Distribution Types Supported
        The simulation engine supports the following probability distributions:
        - **Poisson**: For frequency modeling
        - **Log-Normal**: For severity modeling with heavy tails
        - **Pareto**: For extreme value analysis
        - **Gamma**: For flexible severity distributions
        - **Exponential**: For memoryless processes
        - **Weibull**: For reliability analysis
        - **Negative Binomial**: For overdispersed count data
        - **Binomial**: For bounded discrete events

        ### Getting Started
        1. Register for an account using `/auth/register`
        2. Login to receive your JWT token via `/auth/login`
        3. Create a portfolio using `/portfolio/`
        4. Add policies to your portfolio
        5. Configure and run simulations via `/simulation/run`
        6. View results and generate reports

        For detailed examples and integration guides, visit our documentation.
        ''',
        doc='/docs/',  # Swagger UI endpoint
        authorizations=authorizations,
        security='Bearer',
        contact_email='support@cyberrisk.com',
        contact_url='https://cyberrisk.com/support',
        license='MIT',
        license_url='https://opensource.org/licenses/MIT',
        tags=[
            {'name': 'Authentication', 'description': 'User authentication and account management'},
            {'name': 'Simulation', 'description': 'Monte Carlo simulation operations'},
            {'name': 'Portfolio', 'description': 'Portfolio and policy management'},
            {'name': 'Scenarios', 'description': 'Risk scenario creation and analysis'},
            {'name': 'System', 'description': 'System health and information endpoints'},
        ]
    )
    
    # Create API models for documentation
    models = create_api_models(api)
    
    # Store models in app config for access in blueprints
    app.config['API_MODELS'] = models
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config.get('CORS_ORIGINS', '*'))
    jwt.init_app(app)
    socketio.init_app(
        app, 
        cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'),
        async_mode='eventlet'
    )
    
    # JWT Configuration
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_expired',
            'message': 'The token has expired',
            'timestamp': datetime.utcnow().isoformat()
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'invalid_token',
            'message': 'Invalid token provided',
            'details': str(error),
            'timestamp': datetime.utcnow().isoformat()
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'authorization_required',
            'message': 'Authorization token required',
            'details': str(error),
            'timestamp': datetime.utcnow().isoformat()
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_revoked',
            'message': 'The token has been revoked',
            'timestamp': datetime.utcnow().isoformat()
        }), 401
    
    # Global error handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions with consistent format"""
        logger.error("HTTP Exception", status_code=e.code, description=e.description)
        return jsonify({
            'error': 'http_error',
            'message': e.description,
            'status_code': e.code,
            'timestamp': datetime.utcnow().isoformat()
        }), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Handle unexpected exceptions"""
        logger.error("Unexpected error", error=str(e), exc_info=True)
        return jsonify({
            'error': 'internal_server_error',
            'message': 'An unexpected error occurred',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

    @app.errorhandler(400)
    def handle_bad_request(e):
        """Handle bad request errors"""
        return jsonify({
            'error': 'bad_request',
            'message': 'The request could not be understood or was missing required parameters',
            'timestamp': datetime.utcnow().isoformat()
        }), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle not found errors"""
        return jsonify({
            'error': 'not_found',
            'message': 'The requested resource was not found',
            'timestamp': datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        """Handle validation errors"""
        return jsonify({
            'error': 'validation_error',
            'message': 'The request was well-formed but contains semantic errors',
            'timestamp': datetime.utcnow().isoformat()
        }), 422

    # Request/Response logging middleware
    @app.before_request
    def log_request_info():
        """Log incoming requests"""
        logger.info(
            "Request received",
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            content_length=request.content_length
        )

    @app.after_request
    def log_response_info(response):
        """Log outgoing responses"""
        logger.info(
            "Response sent",
            status_code=response.status_code,
            content_length=response.content_length
        )
        return response
    
    # Security headers middleware
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses"""
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' fonts.googleapis.com cdn.jsdelivr.net; "
            "font-src 'self' fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' ws: wss:;"
        )
        
        # Other security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response
    
    # Health check endpoint (simple, non-documented)
    @app.route('/health')
    def health_check():
        """Simple health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        })
    
    # Register API namespaces (blueprints converted to namespaces)
    from app.api_routes import register_namespaces
    register_namespaces(api, app)
    
    # Log successful initialization
    logger.info(
        "Flask application created successfully",
        config=config_name,
        debug=app.debug,
        cors_origins=app.config.get('CORS_ORIGINS'),
        database_uri=app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'local'
    )
    
    return app


def create_database_tables(app):
    """
    Create database tables within application context
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Create default system configurations if they don't exist
            from app.models import SystemConfiguration
            
            default_configs = [
                {
                    'key': 'max_simulation_iterations',
                    'value': '100000',
                    'description': 'Maximum allowed simulation iterations'
                },
                {
                    'key': 'default_confidence_levels',
                    'value': '[90, 95, 99]',
                    'description': 'Default confidence levels for VaR calculations'
                },
                {
                    'key': 'simulation_timeout_minutes',
                    'value': '30',
                    'description': 'Maximum simulation runtime in minutes'
                },
                {
                    'key': 'max_concurrent_simulations',
                    'value': '5',
                    'description': 'Maximum concurrent simulations per user'
                }
            ]
            
            for config_data in default_configs:
                existing = SystemConfiguration.query.filter_by(key=config_data['key']).first()
                if not existing:
                    config = SystemConfiguration(**config_data)
                    db.session.add(config)
            
            db.session.commit()
            logger.info("Default system configurations created")
            
        except Exception as e:
            logger.error("Failed to create database tables", error=str(e))
            db.session.rollback()
            raise


# Export the global database instance for models
__all__ = ['create_app', 'create_database_tables', 'db', 'socketio', 'api'] 