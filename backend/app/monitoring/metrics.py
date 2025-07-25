"""
Prometheus Metrics Collection System

Provides comprehensive metrics collection for:
- API performance (request duration, throughput, errors)
- Business metrics (simulations, users, portfolios)
- System health (CPU, memory, database connections)
- Custom application metrics
"""

import time
import psutil
from functools import wraps
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter, Histogram, Gauge, Info, 
    generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
)
from flask import Flask, request, g
import structlog

logger = structlog.get_logger(__name__)

class PrometheusMetrics:
    """Prometheus metrics collector for Flask application"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.registry = CollectorRegistry()
        
        # HTTP Request Metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry
        )
        
        self.http_request_size_bytes = Histogram(
            'http_request_size_bytes',
            'HTTP request size in bytes',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.http_response_size_bytes = Histogram(
            'http_response_size_bytes',
            'HTTP response size in bytes',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # System Metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_bytes',
            'System memory usage in bytes',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'System disk usage percentage',
            registry=self.registry
        )
        
        # Database Metrics
        self.database_connections_active = Gauge(
            'database_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.database_query_duration_seconds = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['query_type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )
        
        # Application Info
        self.app_info = Info(
            'app_info',
            'Application information',
            registry=self.registry
        )
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize metrics collection for Flask app"""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        # Set application info
        self.app_info.info({
            'version': app.config.get('VERSION', '1.0.0'),
            'environment': app.config.get('FLASK_ENV', 'production'),
            'name': 'cyber-risk-simulation'
        })
        
        # Start system metrics collection
        self._collect_system_metrics()
    
    def _before_request(self) -> None:
        """Record request start time"""
        g.start_time = time.time()
        
        # Record request size
        if request.content_length:
            endpoint = request.endpoint or 'unknown'
            self.http_request_size_bytes.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(request.content_length)
    
    def _after_request(self, response) -> Any:
        """Record request metrics after processing"""
        if not hasattr(g, 'start_time'):
            return response
        
        duration = time.time() - g.start_time
        endpoint = request.endpoint or 'unknown'
        
        # Record request metrics
        self.http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        
        self.http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
        
        # Record response size
        if hasattr(response, 'content_length') and response.content_length:
            self.http_response_size_bytes.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(response.content_length)
        
        return response
    
    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.system_disk_usage.set(disk_percent)
            
        except Exception as e:
            logger.warning("Failed to collect system metrics", error=str(e))
    
    def track_database_query(self, query_type: str, duration: float) -> None:
        """Track database query performance"""
        self.database_query_duration_seconds.labels(
            query_type=query_type
        ).observe(duration)
    
    def track_database_connections(self, active_connections: int) -> None:
        """Track active database connections"""
        self.database_connections_active.set(active_connections)
    
    def generate_metrics(self) -> str:
        """Generate Prometheus metrics in text format"""
        self._collect_system_metrics()
        return generate_latest(self.registry).decode('utf-8')
    
    def get_content_type(self) -> str:
        """Get Prometheus content type"""
        return CONTENT_TYPE_LATEST


class BusinessMetrics:
    """Business-specific metrics for the cyber risk simulation application"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.registry = CollectorRegistry()
        
        # User Metrics
        self.users_total = Gauge(
            'users_total',
            'Total number of registered users',
            registry=self.registry
        )
        
        self.users_active_24h = Gauge(
            'users_active_24h',
            'Number of active users in last 24 hours',
            registry=self.registry
        )
        
        # Simulation Metrics
        self.simulations_total = Counter(
            'simulations_total',
            'Total number of simulations run',
            ['status'],
            registry=self.registry
        )
        
        self.simulations_duration_seconds = Histogram(
            'simulations_duration_seconds',
            'Simulation execution duration in seconds',
            ['simulation_type'],
            buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600],
            registry=self.registry
        )
        
        self.simulations_iterations = Histogram(
            'simulations_iterations',
            'Number of Monte Carlo iterations per simulation',
            buckets=[1000, 5000, 10000, 25000, 50000, 100000],
            registry=self.registry
        )
        
        # Portfolio Metrics
        self.portfolios_total = Gauge(
            'portfolios_total',
            'Total number of portfolios',
            registry=self.registry
        )
        
        self.portfolio_value_total = Gauge(
            'portfolio_value_total_usd',
            'Total portfolio value in USD',
            registry=self.registry
        )
        
        self.policies_total = Gauge(
            'policies_total',
            'Total number of insurance policies',
            registry=self.registry
        )
        
        # Risk Metrics
        self.risk_var_95 = Gauge(
            'risk_var_95_usd',
            'Value at Risk (95%) in USD',
            ['portfolio_id'],
            registry=self.registry
        )
        
        self.risk_expected_loss = Gauge(
            'risk_expected_loss_usd',
            'Expected Loss in USD',
            ['portfolio_id'],
            registry=self.registry
        )
        
        # API Usage Metrics
        self.api_calls_by_user = Counter(
            'api_calls_by_user_total',
            'Total API calls by user',
            ['user_id', 'endpoint'],
            registry=self.registry
        )
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize business metrics collection"""
        from app.models import db
        self.db = db
        
        # Periodically update business metrics
        self._update_business_metrics()
    
    def _update_business_metrics(self) -> None:
        """Update business metrics from database"""
        try:
            from app.models import User, Portfolio, Policy, SimulationRun
            
            # User metrics
            total_users = User.query.count()
            self.users_total.set(total_users)
            
            # Active users (simplified - would need last_seen field in production)
            # self.users_active_24h.set(active_users_count)
            
            # Portfolio metrics
            total_portfolios = Portfolio.query.count()
            self.portfolios_total.set(total_portfolios)
            
            total_policies = Policy.query.count()
            self.policies_total.set(total_policies)
            
            # Total portfolio value
            portfolios = Portfolio.query.all()
            total_value = sum(p.total_value for p in portfolios if p.total_value)
            self.portfolio_value_total.set(total_value)
            
        except Exception as e:
            logger.warning("Failed to update business metrics", error=str(e))
    
    def track_simulation_start(self, simulation_type: str = 'monte_carlo') -> None:
        """Track simulation start"""
        self.simulations_total.labels(status='started').inc()
    
    def track_simulation_complete(self, duration: float, iterations: int, 
                                simulation_type: str = 'monte_carlo') -> None:
        """Track successful simulation completion"""
        self.simulations_total.labels(status='completed').inc()
        self.simulations_duration_seconds.labels(
            simulation_type=simulation_type
        ).observe(duration)
        self.simulations_iterations.observe(iterations)
    
    def track_simulation_error(self) -> None:
        """Track simulation error"""
        self.simulations_total.labels(status='failed').inc()
    
    def track_risk_metrics(self, portfolio_id: str, var_95: float, 
                          expected_loss: float) -> None:
        """Track calculated risk metrics"""
        self.risk_var_95.labels(portfolio_id=portfolio_id).set(var_95)
        self.risk_expected_loss.labels(portfolio_id=portfolio_id).set(expected_loss)
    
    def track_api_usage(self, user_id: str, endpoint: str) -> None:
        """Track API usage by user"""
        self.api_calls_by_user.labels(
            user_id=user_id,
            endpoint=endpoint
        ).inc()
    
    def generate_metrics(self) -> str:
        """Generate business metrics in Prometheus format"""
        self._update_business_metrics()
        return generate_latest(self.registry).decode('utf-8')


def track_performance(metric_name: str):
    """Decorator to track function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    "Performance tracking",
                    function=func.__name__,
                    metric=metric_name,
                    duration=duration,
                    status="success"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "Performance tracking",
                    function=func.__name__,
                    metric=metric_name,
                    duration=duration,
                    status="error",
                    error=str(e)
                )
                raise
        return wrapper
    return decorator 