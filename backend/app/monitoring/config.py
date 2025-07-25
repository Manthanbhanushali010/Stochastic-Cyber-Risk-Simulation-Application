"""
Monitoring Integration Configuration

This module provides easy integration of all monitoring components
into the Flask application.
"""

import time
from datetime import datetime
from flask import Flask, Response, request, jsonify
from app.monitoring import (
    PrometheusMetrics, BusinessMetrics, HealthChecker, 
    PerformanceProfiler, AlertManager, alert_manager
)

# Global monitoring instances
prometheus_metrics = None
business_metrics = None  
health_checker = None
profiler = None

def init_monitoring(app: Flask) -> None:
    """Initialize all monitoring components for the Flask app"""
    global prometheus_metrics, business_metrics, health_checker, profiler
    
    # Initialize monitoring components
    prometheus_metrics = PrometheusMetrics(app)
    business_metrics = BusinessMetrics(app)
    health_checker = HealthChecker(app)
    profiler = PerformanceProfiler()
    
    # Set start time for uptime monitoring
    app.start_time = datetime.utcnow()
    app.start_timestamp = time.time()
    
    # Register monitoring routes
    register_monitoring_routes(app)

def register_monitoring_routes(app: Flask) -> None:
    """Register monitoring-related routes"""
    
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        # Combine application and business metrics
        app_metrics = prometheus_metrics.generate_metrics()
        business_metrics_data = business_metrics.generate_metrics()
        combined_metrics = app_metrics + "\n\n" + business_metrics_data
        
        return Response(
            combined_metrics,
            mimetype=prometheus_metrics.get_content_type()
        )
    
    @app.route('/api/monitoring/performance')
    def performance_report():
        """Get performance monitoring report"""
        hours = request.args.get('hours', 24, type=int)
        function_name = request.args.get('function')
        return profiler.get_performance_report(
            function_name=function_name, 
            hours=hours
        )
    
    @app.route('/api/monitoring/alerts')
    def active_alerts():
        """Get active alerts with optional filtering"""
        severity = request.args.get('severity')
        source = request.args.get('source')
        severity_enum = None
        
        if severity:
            from app.monitoring.alerts import AlertSeverity
            try:
                severity_enum = AlertSeverity(severity.lower())
            except ValueError:
                pass
        
        alerts = alert_manager.get_active_alerts(
            severity=severity_enum, 
            source=source
        )
        
        return jsonify({
            'alerts': [
                {
                    'id': alert.id,
                    'title': alert.title,
                    'description': alert.description,
                    'severity': alert.severity.value,
                    'source': alert.source,
                    'metric': alert.metric,
                    'value': alert.value,
                    'threshold': alert.threshold,
                    'timestamp': alert.timestamp.isoformat(),
                    'status': alert.status.value,
                    'tags': alert.tags
                }
                for alert in alerts
            ],
            'summary': alert_manager.get_alert_summary()
        })
    
    @app.route('/api/monitoring/alerts/<alert_id>/acknowledge', methods=['POST'])
    def acknowledge_alert(alert_id):
        """Acknowledge an active alert"""
        data = request.get_json() or {}
        acknowledged_by = data.get('acknowledged_by', 'anonymous')
        success = alert_manager.acknowledge_alert(alert_id, acknowledged_by)
        
        if success:
            return jsonify({'message': 'Alert acknowledged successfully'})
        else:
            return jsonify({'error': 'Alert not found'}), 404
    
    @app.route('/api/monitoring/alerts/<alert_id>/resolve', methods=['POST'])
    def resolve_alert(alert_id):
        """Resolve an active alert"""
        data = request.get_json() or {}
        resolved_by = data.get('resolved_by', 'anonymous')
        success = alert_manager.resolve_alert(alert_id, resolved_by)
        
        if success:
            return jsonify({'message': 'Alert resolved successfully'})
        else:
            return jsonify({'error': 'Alert not found'}), 404
    
    @app.route('/api/monitoring/system')
    def system_status():
        """Get comprehensive system status"""
        return jsonify({
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': time.time() - app.start_timestamp,
            'alerts': alert_manager.get_alert_summary(),
            'performance': profiler.get_performance_report(hours=1),
            'health': health_checker._detailed_health()
        })

def get_monitoring_instances():
    """Get monitoring component instances"""
    return {
        'prometheus_metrics': prometheus_metrics,
        'business_metrics': business_metrics,
        'health_checker': health_checker,
        'profiler': profiler,
        'alert_manager': alert_manager
    } 