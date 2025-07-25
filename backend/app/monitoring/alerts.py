"""
Alert Management System

Provides comprehensive alerting capabilities including:
- Real-time alert generation
- Multi-channel notification (email, webhook, log)
- Alert severity levels and escalation
- Alert aggregation and deduplication
- Performance threshold monitoring
"""

import time
import threading
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    """Alert status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    metric: Optional[str] = None
    value: Optional[float] = None
    threshold: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: AlertStatus = AlertStatus.ACTIVE
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

class AlertManager:
    """Comprehensive alert management system"""
    
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notification_channels: List[Callable] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.suppressed_alerts: Set[str] = set()
        self.alert_counts: Dict[AlertSeverity, int] = {
            severity: 0 for severity in AlertSeverity
        }
        self._lock = threading.Lock()
        
        # Default alert rules
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Setup default alerting rules"""
        self.alert_rules = {
            'high_response_time': {
                'metric': 'response_time',
                'threshold': 5.0,
                'severity': AlertSeverity.WARNING,
                'description': 'API response time is above threshold'
            },
            'critical_response_time': {
                'metric': 'response_time',
                'threshold': 10.0,
                'severity': AlertSeverity.CRITICAL,
                'description': 'API response time is critically high'
            },
            'high_memory_usage': {
                'metric': 'memory_usage',
                'threshold': 80.0,
                'severity': AlertSeverity.WARNING,
                'description': 'System memory usage is high'
            },
            'critical_memory_usage': {
                'metric': 'memory_usage',
                'threshold': 95.0,
                'severity': AlertSeverity.CRITICAL,
                'description': 'System memory usage is critically high'
            },
            'high_cpu_usage': {
                'metric': 'cpu_usage',
                'threshold': 80.0,
                'severity': AlertSeverity.WARNING,
                'description': 'System CPU usage is high'
            },
            'critical_cpu_usage': {
                'metric': 'cpu_usage',
                'threshold': 95.0,
                'severity': AlertSeverity.CRITICAL,
                'description': 'System CPU usage is critically high'
            },
            'disk_space_low': {
                'metric': 'disk_usage',
                'threshold': 85.0,
                'severity': AlertSeverity.WARNING,
                'description': 'Disk space is running low'
            },
            'disk_space_critical': {
                'metric': 'disk_usage',
                'threshold': 95.0,
                'severity': AlertSeverity.CRITICAL,
                'description': 'Disk space is critically low'
            },
            'database_connection_failed': {
                'metric': 'database_connectivity',
                'threshold': 0,
                'severity': AlertSeverity.CRITICAL,
                'description': 'Database connection failed'
            },
            'simulation_failure_rate_high': {
                'metric': 'simulation_failure_rate',
                'threshold': 10.0,
                'severity': AlertSeverity.WARNING,
                'description': 'Simulation failure rate is above acceptable threshold'
            }
        }
    
    def create_alert(self, title: str, description: str, severity: AlertSeverity,
                    source: str, metric: Optional[str] = None, 
                    value: Optional[float] = None, threshold: Optional[float] = None,
                    tags: Optional[Dict[str, str]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> Alert:
        """Create a new alert"""
        
        alert_id = f"{source}_{metric or 'general'}_{int(time.time())}"
        
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            source=source,
            metric=metric,
            value=value,
            threshold=threshold,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        with self._lock:
            # Check for duplicate/similar alerts
            similar_alert = self._find_similar_alert(alert)
            if similar_alert:
                logger.info("Similar alert found, updating instead of creating new", 
                          alert_id=alert_id, similar_id=similar_alert.id)
                self._update_alert_occurrence(similar_alert)
                return similar_alert
            
            # Add to active alerts
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            self.alert_counts[severity] += 1
            
            # Keep history size manageable
            if len(self.alert_history) > 10000:
                self.alert_history = self.alert_history[-5000:]
        
        logger.info("Alert created", alert_id=alert_id, severity=severity.value, 
                   title=title, source=source)
        
        # Send notifications
        self._send_notifications(alert)
        
        return alert
    
    def _find_similar_alert(self, new_alert: Alert) -> Optional[Alert]:
        """Find similar active alert to avoid duplicates"""
        for alert in self.active_alerts.values():
            if (alert.source == new_alert.source and 
                alert.metric == new_alert.metric and
                alert.severity == new_alert.severity and
                alert.status == AlertStatus.ACTIVE):
                return alert
        return None
    
    def _update_alert_occurrence(self, alert: Alert) -> None:
        """Update alert occurrence count"""
        if 'occurrence_count' not in alert.metadata:
            alert.metadata['occurrence_count'] = 1
        alert.metadata['occurrence_count'] += 1
        alert.metadata['last_occurrence'] = datetime.utcnow().isoformat()
    
    def resolve_alert(self, alert_id: str, resolved_by: Optional[str] = None) -> bool:
        """Resolve an active alert"""
        with self._lock:
            if alert_id not in self.active_alerts:
                logger.warning("Attempted to resolve non-existent alert", alert_id=alert_id)
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.metadata['resolved_by'] = resolved_by or 'system'
            
            # Remove from active alerts
            del self.active_alerts[alert_id]
            self.alert_counts[alert.severity] -= 1
        
        logger.info("Alert resolved", alert_id=alert_id, resolved_by=resolved_by)
        return True
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an active alert"""
        with self._lock:
            if alert_id not in self.active_alerts:
                logger.warning("Attempted to acknowledge non-existent alert", alert_id=alert_id)
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = acknowledged_by
        
        logger.info("Alert acknowledged", alert_id=alert_id, acknowledged_by=acknowledged_by)
        return True
    
    def suppress_alerts(self, source: str, duration_minutes: int = 60) -> None:
        """Suppress alerts from a specific source"""
        suppression_key = f"{source}_{int(time.time() + duration_minutes * 60)}"
        self.suppressed_alerts.add(suppression_key)
        
        logger.info("Alerts suppressed", source=source, duration_minutes=duration_minutes)
    
    def check_metric_threshold(self, metric: str, value: float, source: str,
                             tags: Optional[Dict[str, str]] = None) -> Optional[Alert]:
        """Check if metric value exceeds threshold and create alert if needed"""
        
        # Check if alerts are suppressed for this source
        current_time = int(time.time())
        active_suppressions = [
            key for key in self.suppressed_alerts 
            if key.startswith(source) and int(key.split('_')[-1]) > current_time
        ]
        
        if active_suppressions:
            return None
        
        # Find applicable alert rules
        triggered_rules = []
        for rule_name, rule in self.alert_rules.items():
            if rule['metric'] == metric:
                if (rule.get('comparison', 'gt') == 'gt' and value > rule['threshold']) or \
                   (rule.get('comparison', 'gt') == 'lt' and value < rule['threshold']):
                    triggered_rules.append((rule_name, rule))
        
        if not triggered_rules:
            return None
        
        # Use the most severe rule
        triggered_rules.sort(key=lambda x: list(AlertSeverity).index(x[1]['severity']), reverse=True)
        rule_name, rule = triggered_rules[0]
        
        return self.create_alert(
            title=f"{metric.replace('_', ' ').title()} Alert",
            description=f"{rule['description']} (Value: {value}, Threshold: {rule['threshold']})",
            severity=rule['severity'],
            source=source,
            metric=metric,
            value=value,
            threshold=rule['threshold'],
            tags=tags or {},
            metadata={'rule': rule_name}
        )
    
    def add_notification_channel(self, channel: Callable[[Alert], None]) -> None:
        """Add a notification channel"""
        self.notification_channels.append(channel)
        logger.info("Notification channel added", channel=channel.__name__)
    
    def _send_notifications(self, alert: Alert) -> None:
        """Send alert notifications to all configured channels"""
        for channel in self.notification_channels:
            try:
                channel(alert)
            except Exception as e:
                logger.error("Failed to send notification", 
                           channel=channel.__name__, error=str(e))
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None,
                         source: Optional[str] = None) -> List[Alert]:
        """Get active alerts with optional filtering"""
        with self._lock:
            alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if source:
            alerts = [a for a in alerts if a.source == source]
        
        # Sort by severity and timestamp
        alerts.sort(key=lambda x: (list(AlertSeverity).index(x.severity), x.timestamp), reverse=True)
        return alerts
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        with self._lock:
            active_count = len(self.active_alerts)
            total_count = len(self.alert_history)
            
            # Count by severity
            severity_counts = {severity.value: 0 for severity in AlertSeverity}
            for alert in self.active_alerts.values():
                severity_counts[alert.severity.value] += 1
            
            # Recent activity (last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recent_alerts = [
                a for a in self.alert_history 
                if a.timestamp > cutoff_time
            ]
            
            # Top sources
            source_counts = {}
            for alert in self.active_alerts.values():
                source_counts[alert.source] = source_counts.get(alert.source, 0) + 1
            
            top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'active_alerts': active_count,
            'total_alerts': total_count,
            'severity_breakdown': severity_counts,
            'recent_alerts_24h': len(recent_alerts),
            'top_alert_sources': top_sources,
            'suppressed_sources': len(self.suppressed_alerts),
            'notification_channels': len(self.notification_channels),
            'last_alert': self.alert_history[-1].timestamp.isoformat() if self.alert_history else None
        }
    
    def cleanup_old_alerts(self, days: int = 30) -> int:
        """Clean up old resolved alerts"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        with self._lock:
            initial_count = len(self.alert_history)
            self.alert_history = [
                a for a in self.alert_history 
                if a.timestamp > cutoff_time or a.status == AlertStatus.ACTIVE
            ]
            removed_count = initial_count - len(self.alert_history)
        
        logger.info("Cleaned up old alerts", removed_count=removed_count, days=days)
        return removed_count
    
    def export_alerts(self, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Export alerts for external analysis"""
        with self._lock:
            alerts_to_export = self.alert_history.copy()
        
        if start_date:
            alerts_to_export = [a for a in alerts_to_export if a.timestamp >= start_date]
        
        if end_date:
            alerts_to_export = [a for a in alerts_to_export if a.timestamp <= end_date]
        
        return [
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
                'tags': alert.tags,
                'metadata': alert.metadata,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'acknowledged_by': alert.acknowledged_by
            }
            for alert in alerts_to_export
        ]


# Global alert manager instance
alert_manager = AlertManager()

# Notification channel implementations
def log_notification_channel(alert: Alert) -> None:
    """Log-based notification channel"""
    logger.info(
        "ALERT NOTIFICATION",
        alert_id=alert.id,
        title=alert.title,
        severity=alert.severity.value,
        source=alert.source,
        description=alert.description,
        value=alert.value,
        threshold=alert.threshold
    )

def webhook_notification_channel(webhook_url: str):
    """Factory for webhook notification channel"""
    def send_webhook(alert: Alert) -> None:
        import requests
        try:
            payload = {
                'alert_id': alert.id,
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity.value,
                'source': alert.source,
                'metric': alert.metric,
                'value': alert.value,
                'threshold': alert.threshold,
                'timestamp': alert.timestamp.isoformat(),
                'tags': alert.tags
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Webhook notification sent", alert_id=alert.id, webhook_url=webhook_url)
            
        except Exception as e:
            logger.error("Failed to send webhook notification", 
                        alert_id=alert.id, webhook_url=webhook_url, error=str(e))
    
    return send_webhook

# Setup default notification channel
alert_manager.add_notification_channel(log_notification_channel) 