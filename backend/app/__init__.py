import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import structlog

from config import get_config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()
socketio = SocketIO()


def create_app(config_name=None):
    """
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Setup security headers
    setup_security_headers(app)
    
    return app


def setup_logging(app):
    """Configure structured logging for the application."""
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format=app.config['LOG_FORMAT']
    )
    
    # Setup structured logging with structlog
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


def initialize_extensions(app):
    """Initialize Flask extensions with the app."""
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)
    socketio.init_app(
        app, 
        cors_allowed_origins=app.config['CORS_ORIGINS'],
        async_mode=app.config['SOCKETIO_ASYNC_MODE']
    )
    
    # JWT configuration
    setup_jwt_handlers(app)


def setup_jwt_handlers(app):
    """Setup JWT token handlers and blacklist functionality."""
    
    # In-memory blacklist for simplicity (use Redis in production)
    blacklist = set()
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in blacklist
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {
            'message': 'The token has been revoked.',
            'error': 'token_revoked'
        }, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {
            'message': 'Signature verification failed.',
            'error': 'invalid_token'
        }, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {
            'message': 'Request does not contain a valid token.',
            'error': 'authorization_required'
        }, 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return {
            'message': 'The token is not fresh.',
            'error': 'fresh_token_required'
        }, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {
            'message': 'The token has expired.',
            'error': 'token_expired'
        }, 401


def register_blueprints(app):
    """Register application blueprints."""
    from app.blueprints.auth import auth_bp
    from app.blueprints.simulation import simulation_bp
    from app.blueprints.portfolio import portfolio_bp
    from app.blueprints.scenarios import scenarios_bp
    from app.blueprints.api import api_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(scenarios_bp, url_prefix='/api/scenarios')
    app.register_blueprint(api_bp, url_prefix='/api')


def setup_error_handlers(app):
    """Setup global error handlers."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'error': 'Bad Request',
            'message': 'The request could not be understood by the server.',
            'status_code': 400
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource.',
            'status_code': 401
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource.',
            'status_code': 403
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Not Found',
            'message': 'The requested resource could not be found.',
            'status_code': 404
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal server error: {error}')
        return {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }, 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f'Unexpected error: {error}')
        db.session.rollback()
        return {
            'error': 'Unexpected Error',
            'message': 'An unexpected error occurred.',
            'status_code': 500
        }, 500


def setup_security_headers(app):
    """Setup security headers for the application."""
    
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses."""
        for header, value in app.config.get('SECURITY_HEADERS', {}).items():
            response.headers[header] = value
        return response


# Import models to ensure they are registered with SQLAlchemy
from app.models import * 