#!/usr/bin/env python3
"""
Flask application entry point for Cyber Risk Simulation Backend.

This module creates and configures the Flask application instance
and provides the entry point for running the server.
"""

import os
import sys
from flask import Flask
from app import create_app, db, socketio

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_application():
    """Create and configure the Flask application."""
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = create_app(config_name)
    
    return app


def initialize_database(app):
    """Initialize the database with tables."""
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("Database tables created successfully")
            
            # Create default system configurations if needed
            from app.models import SystemConfiguration
            
            default_configs = [
                {
                    'key': 'max_simulation_iterations',
                    'value': 1000000,
                    'description': 'Maximum allowed simulation iterations'
                },
                {
                    'key': 'default_frequency_distribution',
                    'value': 'poisson',
                    'description': 'Default frequency distribution for new simulations'
                },
                {
                    'key': 'default_severity_distribution', 
                    'value': 'lognormal',
                    'description': 'Default severity distribution for new simulations'
                },
                {
                    'key': 'simulation_timeout_minutes',
                    'value': 30,
                    'description': 'Maximum simulation runtime in minutes'
                }
            ]
            
            for config_data in default_configs:
                existing_config = SystemConfiguration.query.filter_by(key=config_data['key']).first()
                if not existing_config:
                    config = SystemConfiguration(
                        key=config_data['key'],
                        value=config_data['value'],
                        description=config_data['description']
                    )
                    db.session.add(config)
            
            db.session.commit()
            print("Default system configurations created")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            sys.exit(1)


# Create the Flask application
app = create_application()


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Cyber Risk Simulation Backend")
    print("=" * 60)
    
    # Initialize database
    if len(sys.argv) > 1 and sys.argv[1] == '--init-db':
        print("Initializing database...")
        initialize_database(app)
        sys.exit(0)
    
    # Get runtime configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🌐 Server will run on: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    if debug:
        print("\n📋 Available endpoints will be displayed after startup...")
    
    print("=" * 60)
    
    # Run the application with SocketIO support
    try:
        socketio.run(
            app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            log_output=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Cyber Risk Simulation Backend")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1) 