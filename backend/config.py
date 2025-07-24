import os
from datetime import timedelta
from typing import Type


class Config:
    """Base configuration class with common settings."""
    
    # Flask Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///cyber_risk_sim.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Redis Configuration (for Celery and caching)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL
    
    # SocketIO Configuration
    SOCKETIO_ASYNC_MODE = 'threading'
    
    # Simulation Settings
    MAX_SIMULATION_ITERATIONS = int(os.environ.get('MAX_SIMULATION_ITERATIONS', '1000000'))
    DEFAULT_SIMULATION_ITERATIONS = int(os.environ.get('DEFAULT_SIMULATION_ITERATIONS', '10000'))
    SIMULATION_TIMEOUT = int(os.environ.get('SIMULATION_TIMEOUT', '300'))  # 5 minutes
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    }


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Database - Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cyber_risk_dev.db')
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # CORS - Allow all origins in development
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # Less strict security for development
    SECURITY_HEADERS = {}


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection during testing
    WTF_CSRF_ENABLED = False
    
    # Shorter token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)
    
    # Reduced simulation limits for faster testing
    MAX_SIMULATION_ITERATIONS = 1000
    DEFAULT_SIMULATION_ITERATIONS = 100
    SIMULATION_TIMEOUT = 30  # 30 seconds
    
    # Test Redis (if needed)
    REDIS_URL = 'redis://localhost:6379/1'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production database - PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/cyber_risk_prod'
    
    # Enhanced database settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 20,
        'max_overflow': 30,
    }
    
    # Strict security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Enhanced logging for production
    LOG_LEVEL = 'WARNING'
    
    # Production-specific settings
    PREFERRED_URL_SCHEME = 'https'
    
    # Enable all security headers
    SECURITY_HEADERS = Config.SECURITY_HEADERS


class DockerConfig(Config):
    """Configuration for Docker deployment."""
    
    DEBUG = False
    TESTING = False
    
    # Docker-specific database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@db:5432/cyber_risk'
    
    # Docker-specific Redis URL
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # CORS for containerized frontend
    CORS_ORIGINS = ['http://localhost:3000', 'http://frontend:3000']


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Type[Config]:
    """Get configuration class based on environment name."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default']) 