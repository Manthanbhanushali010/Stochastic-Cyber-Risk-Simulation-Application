"""
Performance Profiler

Provides performance profiling capabilities including:
- Memory usage tracking
- CPU profiling
- Function execution time monitoring
- Performance bottleneck identification
- Resource leak detection
"""

import time
import psutil
import threading
from functools import wraps
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from memory_profiler import profile as memory_profile
import structlog

logger = structlog.get_logger(__name__)

class PerformanceProfiler:
    """Advanced performance profiling system"""
    
    def __init__(self):
        self.profiling_data: Dict[str, List[Dict[str, Any]]] = {}
        self.active_profiles: Dict[str, Dict[str, Any]] = {}
        self.performance_thresholds = {
            'response_time_warning': 1.0,  # seconds
            'response_time_critical': 5.0,  # seconds
            'memory_warning': 500,  # MB
            'memory_critical': 1000,  # MB
            'cpu_warning': 80,  # percent
            'cpu_critical': 95  # percent
        }
        self.monitoring_enabled = True
        self._lock = threading.Lock()
    
    def profile_function(self, function_name: Optional[str] = None):
        """Decorator to profile function execution"""
        def decorator(func: Callable) -> Callable:
            name = function_name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.monitoring_enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                start_memory = self._get_memory_usage()
                start_cpu = psutil.cpu_percent()
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = self._get_memory_usage()
                    end_cpu = psutil.cpu_percent()
                    
                    self._record_performance_data(
                        function_name=name,
                        start_time=start_time,
                        end_time=end_time,
                        duration=end_time - start_time,
                        memory_start=start_memory,
                        memory_end=end_memory,
                        memory_delta=end_memory - start_memory,
                        cpu_start=start_cpu,
                        cpu_end=end_cpu,
                        success=success,
                        error=error,
                        args_count=len(args),
                        kwargs_count=len(kwargs)
                    )
                
                return result
            return wrapper
        return decorator
    
    def start_profiling_session(self, session_name: str) -> str:
        """Start a named profiling session"""
        session_id = f"{session_name}_{int(time.time())}"
        
        with self._lock:
            self.active_profiles[session_id] = {
                'name': session_name,
                'start_time': time.time(),
                'start_memory': self._get_memory_usage(),
                'start_cpu': psutil.cpu_percent(),
                'function_calls': []
            }
        
        logger.info("Started profiling session", session_id=session_id)
        return session_id
    
    def end_profiling_session(self, session_id: str) -> Dict[str, Any]:
        """End a profiling session and return results"""
        with self._lock:
            if session_id not in self.active_profiles:
                raise ValueError(f"Profiling session {session_id} not found")
            
            session = self.active_profiles[session_id]
            end_time = time.time()
            end_memory = self._get_memory_usage()
            end_cpu = psutil.cpu_percent()
            
            results = {
                'session_id': session_id,
                'name': session['name'],
                'duration': end_time - session['start_time'],
                'memory_delta': end_memory - session['start_memory'],
                'cpu_delta': end_cpu - session['start_cpu'],
                'function_calls': len(session['function_calls']),
                'start_time': datetime.fromtimestamp(session['start_time']).isoformat(),
                'end_time': datetime.fromtimestamp(end_time).isoformat(),
                'performance_summary': self._analyze_session_performance(session)
            }
            
            # Clean up
            del self.active_profiles[session_id]
            
        logger.info("Ended profiling session", session_id=session_id, results=results)
        return results
    
    def _record_performance_data(self, **data) -> None:
        """Record performance data for analysis"""
        timestamp = datetime.utcnow().isoformat()
        function_name = data.get('function_name', 'unknown')
        
        performance_record = {
            'timestamp': timestamp,
            **data
        }
        
        with self._lock:
            if function_name not in self.profiling_data:
                self.profiling_data[function_name] = []
            
            self.profiling_data[function_name].append(performance_record)
            
            # Keep only last 1000 records per function to prevent memory issues
            if len(self.profiling_data[function_name]) > 1000:
                self.profiling_data[function_name] = self.profiling_data[function_name][-1000:]
            
            # Check for performance issues
            self._check_performance_thresholds(performance_record)
    
    def _check_performance_thresholds(self, record: Dict[str, Any]) -> None:
        """Check if performance thresholds are exceeded"""
        function_name = record.get('function_name', 'unknown')
        duration = record.get('duration', 0)
        memory_delta = record.get('memory_delta', 0)
        
        alerts = []
        
        # Check response time
        if duration > self.performance_thresholds['response_time_critical']:
            alerts.append({
                'level': 'critical',
                'metric': 'response_time',
                'value': duration,
                'threshold': self.performance_thresholds['response_time_critical'],
                'message': f"Critical response time: {duration:.2f}s"
            })
        elif duration > self.performance_thresholds['response_time_warning']:
            alerts.append({
                'level': 'warning',
                'metric': 'response_time',
                'value': duration,
                'threshold': self.performance_thresholds['response_time_warning'],
                'message': f"Slow response time: {duration:.2f}s"
            })
        
        # Check memory usage
        memory_mb = memory_delta
        if memory_mb > self.performance_thresholds['memory_critical']:
            alerts.append({
                'level': 'critical',
                'metric': 'memory_usage',
                'value': memory_mb,
                'threshold': self.performance_thresholds['memory_critical'],
                'message': f"Critical memory usage: {memory_mb:.1f}MB"
            })
        elif memory_mb > self.performance_thresholds['memory_warning']:
            alerts.append({
                'level': 'warning',
                'metric': 'memory_usage',
                'value': memory_mb,
                'threshold': self.performance_thresholds['memory_warning'],
                'message': f"High memory usage: {memory_mb:.1f}MB"
            })
        
        # Log alerts
        for alert in alerts:
            logger.warning(
                "Performance threshold exceeded",
                function=function_name,
                **alert
            )
    
    def _analyze_session_performance(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance data for a session"""
        calls = session.get('function_calls', [])
        
        if not calls:
            return {'message': 'No function calls recorded'}
        
        total_duration = sum(call.get('duration', 0) for call in calls)
        avg_duration = total_duration / len(calls) if calls else 0
        
        slowest_call = max(calls, key=lambda x: x.get('duration', 0), default={})
        fastest_call = min(calls, key=lambda x: x.get('duration', 0), default={})
        
        return {
            'total_calls': len(calls),
            'total_duration': total_duration,
            'average_duration': avg_duration,
            'slowest_call': {
                'function': slowest_call.get('function_name', 'unknown'),
                'duration': slowest_call.get('duration', 0)
            },
            'fastest_call': {
                'function': fastest_call.get('function_name', 'unknown'),
                'duration': fastest_call.get('duration', 0)
            }
        }
    
    def get_performance_report(self, function_name: Optional[str] = None, 
                             hours: int = 24) -> Dict[str, Any]:
        """Generate performance report"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self._lock:
            if function_name:
                functions_to_analyze = [function_name] if function_name in self.profiling_data else []
            else:
                functions_to_analyze = list(self.profiling_data.keys())
            
            report = {
                'generated_at': datetime.utcnow().isoformat(),
                'time_window_hours': hours,
                'functions_analyzed': len(functions_to_analyze),
                'functions': {}
            }
            
            for func_name in functions_to_analyze:
                records = [
                    r for r in self.profiling_data[func_name]
                    if datetime.fromisoformat(r['timestamp']) > cutoff_time
                ]
                
                if not records:
                    continue
                
                durations = [r['duration'] for r in records]
                memory_deltas = [r['memory_delta'] for r in records]
                success_count = sum(1 for r in records if r.get('success', True))
                
                report['functions'][func_name] = {
                    'call_count': len(records),
                    'success_rate': success_count / len(records) if records else 0,
                    'avg_duration': sum(durations) / len(durations) if durations else 0,
                    'max_duration': max(durations) if durations else 0,
                    'min_duration': min(durations) if durations else 0,
                    'avg_memory_delta': sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0,
                    'max_memory_delta': max(memory_deltas) if memory_deltas else 0,
                    'performance_issues': self._identify_performance_issues(records)
                }
        
        return report
    
    def _identify_performance_issues(self, records: List[Dict[str, Any]]) -> List[str]:
        """Identify performance issues from records"""
        issues = []
        
        if not records:
            return issues
        
        # Check for consistently slow performance
        slow_calls = [r for r in records if r['duration'] > self.performance_thresholds['response_time_warning']]
        if len(slow_calls) > len(records) * 0.1:  # More than 10% of calls are slow
            issues.append(f"Consistently slow performance: {len(slow_calls)}/{len(records)} calls exceed {self.performance_thresholds['response_time_warning']}s")
        
        # Check for memory leaks
        memory_deltas = [r['memory_delta'] for r in records[-10:]]  # Last 10 calls
        if len(memory_deltas) >= 5 and all(delta > 0 for delta in memory_deltas):
            issues.append("Potential memory leak: consistent memory growth detected")
        
        # Check for high error rate
        error_count = sum(1 for r in records if not r.get('success', True))
        error_rate = error_count / len(records)
        if error_rate > 0.05:  # More than 5% error rate
            issues.append(f"High error rate: {error_rate:.1%} ({error_count}/{len(records)} calls)")
        
        return issues
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0
    
    def clear_profiling_data(self, function_name: Optional[str] = None) -> None:
        """Clear profiling data"""
        with self._lock:
            if function_name:
                if function_name in self.profiling_data:
                    del self.profiling_data[function_name]
                    logger.info("Cleared profiling data", function=function_name)
            else:
                self.profiling_data.clear()
                logger.info("Cleared all profiling data")
    
    def set_threshold(self, metric: str, value: float) -> None:
        """Set performance threshold"""
        if metric in self.performance_thresholds:
            self.performance_thresholds[metric] = value
            logger.info("Updated performance threshold", metric=metric, value=value)
        else:
            raise ValueError(f"Unknown threshold metric: {metric}")
    
    def enable_monitoring(self) -> None:
        """Enable performance monitoring"""
        self.monitoring_enabled = True
        logger.info("Performance monitoring enabled")
    
    def disable_monitoring(self) -> None:
        """Disable performance monitoring"""
        self.monitoring_enabled = False
        logger.info("Performance monitoring disabled")


# Global profiler instance
profiler = PerformanceProfiler()

# Convenience decorators
def profile_performance(function_name: Optional[str] = None):
    """Convenience decorator for profiling functions"""
    return profiler.profile_function(function_name)

def profile_memory(func: Callable) -> Callable:
    """Decorator for memory profiling using memory_profiler"""
    return memory_profile(func) 