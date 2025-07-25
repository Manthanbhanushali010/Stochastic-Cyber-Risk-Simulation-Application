"""
Health Check System

Provides comprehensive health monitoring for:
- Database connectivity
- External service availability
- System resource utilization
- Application component health
- Custom health checks
"""

import time
import psutil
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
from flask import Flask, current_app
from healthcheck import HealthCheck, EnvironmentDump
import structlog

logger = structlog.get_logger(__name__)

class HealthChecker:
    """Comprehensive health monitoring system"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.health_check = HealthCheck()
        self.env_dump = EnvironmentDump()
        self.custom_checks: Dict[str, Callable] = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask) -> None:
        """Initialize health checks for Flask app"""
        # Register default health checks
        self.health_check.add_check(self._database_health)
        self.health_check.add_check(self._memory_health)
        self.health_check.add_check(self._disk_health)
        self.health_check.add_check(self._cpu_health)
        
        # Register environment dump info
        self.env_dump.add_section("application", self._get_app_info)
        self.env_dump.add_section("system", self._get_system_info)
        self.env_dump.add_section("database", self._get_database_info)
        
        # Add health check routes
        app.add_url_rule('/health', 'health', self.health_check.run)
        app.add_url_rule('/environment', 'environment', self.env_dump.run)
        app.add_url_rule('/health/detailed', 'health_detailed', self._detailed_health)
        app.add_url_rule('/health/readiness', 'readiness', self._readiness_check)
        app.add_url_rule('/health/liveness', 'liveness', self._liveness_check)
    
    def _database_health(self) -> bool:
        """Check database connectivity"""
        try:
            from app.models import db
            # Simple query to test database connectivity
            db.session.execute('SELECT 1')
            db.session.commit()
            return True, "Database connection successful"
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False, f"Database connection failed: {str(e)}"
    
    def _memory_health(self) -> bool:
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            if memory_percent > 90:
                return False, f"High memory usage: {memory_percent:.1f}%"
            elif memory_percent > 80:
                return True, f"Warning: Memory usage at {memory_percent:.1f}%"
            else:
                return True, f"Memory usage normal: {memory_percent:.1f}%"
        except Exception as e:
            logger.error("Memory health check failed", error=str(e))
            return False, f"Memory check failed: {str(e)}"
    
    def _disk_health(self) -> bool:
        """Check disk space usage"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 90:
                return False, f"High disk usage: {disk_percent:.1f}%"
            elif disk_percent > 80:
                return True, f"Warning: Disk usage at {disk_percent:.1f}%"
            else:
                return True, f"Disk usage normal: {disk_percent:.1f}%"
        except Exception as e:
            logger.error("Disk health check failed", error=str(e))
            return False, f"Disk check failed: {str(e)}"
    
    def _cpu_health(self) -> bool:
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 95:
                return False, f"High CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                return True, f"Warning: CPU usage at {cpu_percent:.1f}%"
            else:
                return True, f"CPU usage normal: {cpu_percent:.1f}%"
        except Exception as e:
            logger.error("CPU health check failed", error=str(e))
            return False, f"CPU check failed: {str(e)}"
    
    def _get_app_info(self) -> Dict[str, Any]:
        """Get application information"""
        return {
            "name": "Cyber Risk Simulation Application",
            "version": current_app.config.get('VERSION', '1.0.0'),
            "environment": current_app.config.get('FLASK_ENV', 'production'),
            "started_at": getattr(current_app, 'start_time', datetime.utcnow().isoformat()),
            "uptime_seconds": time.time() - getattr(current_app, 'start_timestamp', time.time()),
            "debug_mode": current_app.debug,
            "testing_mode": current_app.testing
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total) * 100, 2),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
        except Exception as e:
            logger.error("Failed to get system info", error=str(e))
            return {"error": str(e)}
    
    def _get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            from app.models import db, User, Portfolio, SimulationRun
            
            # Get table counts
            user_count = User.query.count()
            portfolio_count = Portfolio.query.count()
            simulation_count = SimulationRun.query.count()
            
            # Get database connection info
            engine = db.engine
            pool = engine.pool
            
            return {
                "database_url": str(engine.url).split('@')[0] + '@***',  # Hide credentials
                "pool_size": pool.size(),
                "checked_in_connections": pool.checkedin(),
                "checked_out_connections": pool.checkedout(),
                "table_counts": {
                    "users": user_count,
                    "portfolios": portfolio_count,
                    "simulations": simulation_count
                }
            }
        except Exception as e:
            logger.error("Failed to get database info", error=str(e))
            return {"error": str(e)}
    
    def _detailed_health(self) -> Dict[str, Any]:
        """Detailed health check with component status"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": {},
                "summary": {
                    "total_checks": 0,
                    "passed": 0,
                    "failed": 0,
                    "warnings": 0
                }
            }
            
            # Run all health checks
            checks = [
                ("database", self._database_health),
                ("memory", self._memory_health),
                ("disk", self._disk_health),
                ("cpu", self._cpu_health)
            ]
            
            # Add custom checks
            for name, check_func in self.custom_checks.items():
                checks.append((name, check_func))
            
            for check_name, check_func in checks:
                try:
                    success, message = check_func()
                    health_status["checks"][check_name] = {
                        "status": "pass" if success else "fail",
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    health_status["summary"]["total_checks"] += 1
                    if success:
                        if "warning" in message.lower():
                            health_status["summary"]["warnings"] += 1
                        else:
                            health_status["summary"]["passed"] += 1
                    else:
                        health_status["summary"]["failed"] += 1
                        health_status["status"] = "unhealthy"
                        
                except Exception as e:
                    health_status["checks"][check_name] = {
                        "status": "error",
                        "message": f"Health check error: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    health_status["summary"]["total_checks"] += 1
                    health_status["summary"]["failed"] += 1
                    health_status["status"] = "unhealthy"
            
            return health_status
            
        except Exception as e:
            logger.error("Detailed health check failed", error=str(e))
            return {
                "status": "error",
                "message": f"Health check system error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _readiness_check(self) -> Dict[str, Any]:
        """Kubernetes readiness probe - check if app is ready to serve traffic"""
        try:
            # Check critical components for readiness
            db_ok, db_msg = self._database_health()
            
            if not db_ok:
                return {
                    "status": "not_ready",
                    "message": "Database not available",
                    "details": db_msg
                }, 503
            
            return {
                "status": "ready",
                "message": "Application ready to serve traffic",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Readiness check failed", error=str(e))
            return {
                "status": "not_ready", 
                "message": f"Readiness check error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }, 503
    
    def _liveness_check(self) -> Dict[str, Any]:
        """Kubernetes liveness probe - check if app is alive"""
        try:
            # Simple liveness check - if we can respond, we're alive
            return {
                "status": "alive",
                "message": "Application is running",
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": time.time() - getattr(current_app, 'start_timestamp', time.time())
            }
        except Exception as e:
            logger.error("Liveness check failed", error=str(e))
            return {
                "status": "dead",
                "message": f"Liveness check error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }, 503
    
    def add_custom_check(self, name: str, check_func: Callable) -> None:
        """Add a custom health check function"""
        self.custom_checks[name] = check_func
        logger.info("Added custom health check", check_name=name)
    
    def remove_custom_check(self, name: str) -> None:
        """Remove a custom health check"""
        if name in self.custom_checks:
            del self.custom_checks[name]
            logger.info("Removed custom health check", check_name=name) 