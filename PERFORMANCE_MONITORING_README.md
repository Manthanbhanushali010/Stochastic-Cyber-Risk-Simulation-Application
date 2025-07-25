# Performance Monitoring & Alerting System

## Overview

The Cyber Risk Simulation Application includes a comprehensive performance monitoring and alerting system designed for enterprise-grade observability. This system provides real-time insights into application performance, system health, and business metrics.

## Architecture

### Components

1. **Prometheus Metrics Collection**
   - Application performance metrics (response times, throughput, errors)
   - System resource metrics (CPU, memory, disk usage)
   - Business metrics (simulations, portfolios, risk calculations)
   - Database performance metrics

2. **Grafana Dashboards**
   - Real-time visualization of metrics
   - Interactive dashboards for different stakeholders
   - Alerting integration with visual indicators

3. **AlertManager**
   - Intelligent alert routing and grouping
   - Multi-channel notifications (email, webhook, Slack)
   - Alert suppression and acknowledgment
   - Escalation policies

4. **Performance Profiler**
   - Function-level performance tracking
   - Memory usage analysis
   - Performance bottleneck identification
   - Resource leak detection

## Key Features

### 🎯 **Application Performance Monitoring (APM)**
- HTTP request metrics (rate, duration, size)
- Error rate tracking with detailed categorization
- Response time percentiles (50th, 95th, 99th)
- Custom business logic performance tracking

### 📊 **System Health Monitoring**
- CPU, Memory, and Disk utilization
- Database connection pool monitoring
- System uptime and availability tracking
- Container resource usage (via cAdvisor)

### 🏢 **Business Metrics**
- Total users and active user counts
- Simulation execution metrics (count, duration, success rate)
- Portfolio value and policy counts
- Risk metrics (VaR, Expected Loss) by portfolio
- API usage patterns by user

### 🚨 **Intelligent Alerting**
- **Severity Levels**: INFO, WARNING, CRITICAL, EMERGENCY
- **Multi-condition Rules**: Complex threshold combinations
- **Alert Deduplication**: Prevents alert spam
- **Auto-resolution**: Automatically resolves alerts when conditions improve

## Deployment

### Docker Compose Setup

```bash
# Start the monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Verify services are running
docker-compose ps
```

### Accessing Monitoring Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3001 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | No auth |
| **AlertManager** | http://localhost:9093 | No auth |
| **Application** | http://localhost:3000 | Register/Login |

## Metrics Reference

### Application Metrics

```prometheus
# HTTP Request Metrics
http_requests_total{method, endpoint, status_code}
http_request_duration_seconds{method, endpoint}
http_request_size_bytes{method, endpoint}
http_response_size_bytes{method, endpoint}

# System Metrics  
system_cpu_usage_percent
system_memory_usage_bytes
system_disk_usage_percent

# Database Metrics
database_connections_active
database_query_duration_seconds{query_type}

# Business Metrics
users_total
users_active_24h
simulations_total{status}
simulations_duration_seconds{simulation_type}
portfolios_total
portfolio_value_total_usd
risk_var_95_usd{portfolio_id}
risk_expected_loss_usd{portfolio_id}
```

### Custom Metrics Collection

```python
from app.monitoring import prometheus_metrics, business_metrics, profiler

# Track custom application metrics
@profiler.profile_function("simulation_engine")
def run_monte_carlo_simulation():
    # Your simulation logic
    pass

# Track business events
business_metrics.track_simulation_complete(
    duration=120.5,
    iterations=10000,
    simulation_type="monte_carlo"
)

# Check performance thresholds
alert_manager.check_metric_threshold(
    metric="response_time",
    value=2.5,
    source="api_endpoint"
)
```

## Alert Rules

### System Alerts

| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| **High CPU Usage** | >80% | 5min | WARNING |
| **Critical CPU Usage** | >95% | 2min | CRITICAL |
| **High Memory Usage** | >6GB | 5min | WARNING |
| **Critical Memory Usage** | >7GB | 2min | CRITICAL |
| **High Disk Usage** | >85% | 10min | WARNING |
| **Critical Disk Usage** | >95% | 5min | CRITICAL |

### Application Alerts

| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| **High Response Time** | >2s (95th percentile) | 5min | WARNING |
| **Critical Response Time** | >5s (95th percentile) | 2min | CRITICAL |
| **High Error Rate** | >5% | 5min | WARNING |
| **Critical Error Rate** | >10% | 2min | CRITICAL |
| **Database Slow Queries** | >1s (95th percentile) | 5min | WARNING |

### Business Logic Alerts

| Alert | Threshold | Duration | Severity |
|-------|-----------|----------|----------|
| **Simulation Failure Rate** | >10% | 5min | WARNING |
| **No Simulations Running** | 0 simulations | 30min | WARNING |
| **Service Down** | Health check failing | 1min | CRITICAL |

## API Endpoints

### Monitoring APIs

```bash
# Get Prometheus metrics
GET /metrics

# Performance report
GET /api/monitoring/performance?hours=24&function=simulation_engine

# Active alerts
GET /api/monitoring/alerts?severity=critical&source=database

# Acknowledge alert
POST /api/monitoring/alerts/{alert_id}/acknowledge
{
  "acknowledged_by": "admin@company.com"
}

# Resolve alert
POST /api/monitoring/alerts/{alert_id}/resolve
{
  "resolved_by": "system_admin"
}

# System status
GET /api/monitoring/system
```

### Health Check Endpoints

```bash
# Basic health check
GET /health

# Detailed health check
GET /health/detailed

# Kubernetes readiness probe
GET /health/readiness

# Kubernetes liveness probe  
GET /health/liveness

# Environment information
GET /environment
```

## Grafana Dashboards

### Application Dashboard
- **HTTP Request Rate**: Real-time request throughput
- **Response Time**: 95th and 50th percentile response times
- **Error Rate**: Application error percentage
- **System Resources**: CPU, Memory, Disk usage
- **Active Users**: Current active user count
- **Database Performance**: Connection pool and query metrics

### Business Intelligence Dashboard
- **Simulation Metrics**: Execution rate and success/failure ratios
- **Portfolio Analytics**: Total value and policy distributions
- **Risk Metrics**: VaR and Expected Loss by portfolio
- **User Activity**: Registration trends and API usage patterns

### Infrastructure Dashboard
- **Container Metrics**: Resource usage per container
- **Network Performance**: Request/response latencies
- **Database Health**: Connection counts and query performance
- **System Overview**: Overall infrastructure health

## Performance Optimization

### Best Practices

1. **Metric Collection**
   ```python
   # Use sampling for high-frequency metrics
   if random.random() < 0.1:  # Sample 10% of requests
       profiler.profile_function("high_frequency_function")
   ```

2. **Alert Tuning**
   ```yaml
   # Use appropriate time windows
   - alert: HighResponseTime
     expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
     for: 5m  # Avoid flapping alerts
   ```

3. **Resource Management**
   ```python
   # Limit profiling data retention
   profiler.clear_profiling_data(function_name="old_function")
   
   # Clean up old alerts
   alert_manager.cleanup_old_alerts(days=30)
   ```

## Troubleshooting

### Common Issues

#### High Memory Usage in Monitoring
```bash
# Check Prometheus storage usage
du -sh /var/lib/docker/volumes/prometheus_data

# Reduce retention period
--storage.tsdb.retention.time=168h  # 7 days instead of default
```

#### Missing Metrics
```bash
# Verify application is exposing metrics
curl http://localhost:5000/metrics

# Check Prometheus targets
curl http://localhost:9090/api/v1/targets
```

#### Alerts Not Firing
```bash
# Validate alert rules
promtool check rules monitoring/prometheus/alerts.yml

# Check AlertManager configuration
curl http://localhost:9093/api/v1/status
```

### Debug Commands

```bash
# View application logs
docker-compose logs -f backend

# Check Prometheus configuration
docker exec prometheus cat /etc/prometheus/prometheus.yml

# Grafana data source health
curl -H "Authorization: Bearer $GRAFANA_TOKEN" \
     http://localhost:3001/api/datasources/1/health
```

## Security Considerations

### Metrics Security
- Metrics endpoints are publicly accessible but contain no sensitive data
- Use network segmentation in production
- Consider authentication for Grafana and Prometheus in production

### Data Privacy
- Business metrics are aggregated and anonymized
- No personally identifiable information (PII) in metrics
- User IDs are hashed in tracking metrics

### Access Control
```python
# Production configuration
MONITORING_AUTH_REQUIRED = True
METRICS_ACCESS_TOKEN = "secure-token-here"
GRAFANA_SECURITY_ENABLED = True
```

## Advanced Configuration

### Custom Notification Channels

```python
# Slack webhook integration
def slack_notification_channel(webhook_url):
    def send_slack(alert):
        payload = {
            "text": f"🚨 {alert.title}",
            "attachments": [{
                "color": "danger" if alert.severity.value == "critical" else "warning",
                "fields": [
                    {"title": "Severity", "value": alert.severity.value, "short": True},
                    {"title": "Source", "value": alert.source, "short": True},
                    {"title": "Description", "value": alert.description, "short": False}
                ]
            }]
        }
        requests.post(webhook_url, json=payload)
    return send_slack

# Register the channel
alert_manager.add_notification_channel(
    slack_notification_channel("https://hooks.slack.com/services/...")
)
```

### Performance Profiling Sessions

```python
# Profile a complex operation
session_id = profiler.start_profiling_session("portfolio_analysis")

try:
    # Run your complex operation
    analyze_portfolio_risk(portfolio_id)
finally:
    results = profiler.end_profiling_session(session_id)
    print(f"Analysis took {results['duration']:.2f}s")
```

## Production Deployment

### Scaling Considerations
- **Prometheus**: Configure federation for multi-region deployments
- **Grafana**: Use external database (PostgreSQL) for dashboard persistence
- **AlertManager**: Set up clustering for high availability

### Backup Strategy
```bash
# Backup Prometheus data
docker run --rm -v prometheus_data:/source -v /backup:/backup alpine \
  tar czf /backup/prometheus-$(date +%Y%m%d).tar.gz -C /source .

# Backup Grafana dashboards
curl -H "Authorization: Bearer $GRAFANA_TOKEN" \
     http://localhost:3001/api/search?type=dash-db | \
     jq -r '.[].uri' | \
     xargs -I{} curl -H "Authorization: Bearer $GRAFANA_TOKEN" \
     http://localhost:3001/api/dashboards/{} > grafana-backup.json
```

### Monitoring the Monitoring System
- Set up external monitoring for Prometheus availability
- Monitor Grafana dashboard load times
- Track AlertManager notification delivery rates

---

## Support

For technical support or questions about the monitoring system:

- **Email**: monitoring-support@cyberrisk.com
- **Documentation**: https://docs.cyberrisk.com/monitoring
- **GitHub Issues**: https://github.com/your-org/cyber-risk-simulation/issues

## License

This monitoring system is part of the Cyber Risk Simulation Application and is licensed under the MIT License. 