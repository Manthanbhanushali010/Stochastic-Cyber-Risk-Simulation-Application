# 🌐 Production Deployment Guide
## Stochastic Cyber Risk Simulation Application

This guide provides step-by-step instructions for deploying the complete enterprise-grade cyber risk simulation platform to production.

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx Load Balancer]
    end
    
    subgraph "Frontend Tier"
        FE1[React App Instance 1]
        FE2[React App Instance 2]
    end
    
    subgraph "Backend Tier"
        BE1[Flask API Instance 1]
        BE2[Flask API Instance 2]
        BE3[Flask API Instance 3]
    end
    
    subgraph "Database Tier"
        DB[(PostgreSQL Primary)]
        DB_REPLICA[(PostgreSQL Replica)]
    end
    
    subgraph "Cache & Queue"
        REDIS[(Redis Cluster)]
        CELERY[Celery Workers]
    end
    
    subgraph "Monitoring Stack"
        PROM[Prometheus]
        GRAF[Grafana]
        ALERT[AlertManager]
    end
    
    LB --> FE1
    LB --> FE2
    FE1 --> BE1
    FE2 --> BE2
    BE1 --> DB
    BE2 --> DB
    BE3 --> DB_REPLICA
    BE1 --> REDIS
    BE2 --> REDIS
    CELERY --> REDIS
    PROM --> BE1
    PROM --> BE2
    PROM --> BE3
    GRAF --> PROM
    ALERT --> PROM
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Domain name and SSL certificates
- At least 8GB RAM, 4 CPU cores, 100GB storage

### 1. Clone & Configure
```bash
git clone https://github.com/Manthanbhanushali010/Stochastic-Cyber-Risk-Simulation-Application.git
cd Stochastic-Cyber-Risk-Simulation-Application

# Copy environment templates
cp .env.example .env.prod
cp backend/.env.example backend/.env.prod
cp frontend/.env.example frontend/.env.prod
```

### 2. Production Environment Setup
```bash
# Edit production configuration
nano .env.prod
```

```env
# Production Environment Configuration
COMPOSE_FILE=docker-compose.yml:docker-compose.prod.yml:docker-compose.monitoring.yml
FLASK_ENV=production
NODE_ENV=production

# Database
DATABASE_URL=postgresql://cyber_user:secure_password@postgres:5432/cyber_risk_prod
POSTGRES_DB=cyber_risk_prod
POSTGRES_USER=cyber_user
POSTGRES_PASSWORD=secure_password_here

# Security
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Redis
REDIS_URL=redis://redis:6379/0

# Monitoring
GRAFANA_ADMIN_PASSWORD=secure_grafana_password
PROMETHEUS_RETENTION=30d

# SSL/HTTPS
SSL_CERTIFICATE_PATH=/etc/ssl/certs/cyber-risk.crt
SSL_PRIVATE_KEY_PATH=/etc/ssl/private/cyber-risk.key
```

### 3. Deploy with Monitoring
```bash
# Start all services including monitoring
docker-compose --env-file .env.prod up -d

# Verify deployment
docker-compose ps
```

## 🔧 Service Configuration

### Frontend Configuration (`frontend/.env.prod`)
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

### Backend Configuration (`backend/.env.prod`)
```env
FLASK_ENV=production
DATABASE_URL=postgresql://cyber_user:secure_password@postgres:5432/cyber_risk_prod
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 🌐 Domain & SSL Setup

### 1. DNS Configuration
```dns
# A Records
yourdomain.com          → Your_Server_IP
www.yourdomain.com      → Your_Server_IP
api.yourdomain.com      → Your_Server_IP
monitoring.yourdomain.com → Your_Server_IP
```

### 2. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com -d monitoring.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 3 * * * certbot renew --quiet --no-self-upgrade
```

## 🐳 Production Docker Configuration

### `docker-compose.prod.yml`
```yaml
version: '3.8'

services:
  backend:
    environment:
      - FLASK_ENV=production
      - GUNICORN_WORKERS=4
      - GUNICORN_THREADS=2
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    restart: unless-stopped

  frontend:
    environment:
      - NODE_ENV=production
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  postgres:
    environment:
      - POSTGRES_DB=cyber_risk_prod
      - POSTGRES_USER=cyber_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    restart: unless-stopped

volumes:
  postgres_prod_data:
    driver: local
```

## 🔒 Security Hardening

### 1. Firewall Configuration
```bash
# UFW Firewall Setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Docker Security
```bash
# Create dedicated user
sudo useradd -r -s /bin/false cyberrisk
sudo usermod -aG docker cyberrisk

# Set file permissions
sudo chown -R cyberrisk:cyberrisk /opt/cyber-risk-app
sudo chmod 750 /opt/cyber-risk-app
```

### 3. Database Security
```sql
-- PostgreSQL Security
CREATE ROLE cyber_readonly;
GRANT CONNECT ON DATABASE cyber_risk_prod TO cyber_readonly;
GRANT USAGE ON SCHEMA public TO cyber_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cyber_readonly;

-- Create monitoring user
CREATE USER monitoring_user WITH PASSWORD 'monitoring_password';
GRANT cyber_readonly TO monitoring_user;
```

## 📊 Monitoring Setup

### 1. Grafana Configuration
```bash
# Access Grafana
https://monitoring.yourdomain.com:3001
# Login: admin / secure_grafana_password

# Import dashboards
# - Application Performance Dashboard
# - Infrastructure Monitoring Dashboard  
# - Business Intelligence Dashboard
```

### 2. Prometheus Targets
```yaml
# Additional production targets
scrape_configs:
  - job_name: 'cyber-risk-production'
    static_configs:
      - targets: ['backend:5000', 'backend-2:5000', 'backend-3:5000']
    
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### 3. AlertManager Notifications
```yaml
# Slack Integration
receivers:
  - name: 'slack-alerts'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#cyber-risk-alerts'
        title: 'Cyber Risk Alert'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

# Email Integration  
  - name: 'email-alerts'
    email_configs:
      - to: 'ops-team@company.com'
        from: 'alerts@yourdomain.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@yourdomain.com'
        auth_password: 'app_password'
        subject: 'Cyber Risk System Alert'
```

## 🔄 Backup & Recovery

### 1. Database Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# PostgreSQL Backup
docker exec postgres pg_dump -U cyber_user cyber_risk_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Compress and encrypt
gzip $BACKUP_DIR/db_backup_$DATE.sql
gpg --cipher-algo AES256 --compress-algo 1 --symmetric --output $BACKUP_DIR/db_backup_$DATE.sql.gz.gpg $BACKUP_DIR/db_backup_$DATE.sql.gz

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -name "db_backup_*.gpg" -mtime +30 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_backup_$DATE.sql.gz.gpg s3://your-backup-bucket/
```

### 2. Application State Backup
```bash
#!/bin/bash
# backup_app_state.sh
DATE=$(date +%Y%m%d_%H%M%S)

# Backup uploaded files
tar -czf /backups/uploads_$DATE.tar.gz /app/uploads/

# Backup configuration
tar -czf /backups/config_$DATE.tar.gz \
    .env.prod \
    backend/.env.prod \
    frontend/.env.prod \
    nginx/ \
    monitoring/

# Backup Grafana dashboards
docker exec grafana grafana-cli admin export-dashboard > /backups/grafana_dashboards_$DATE.json
```

### 3. Automated Backup Schedule
```cron
# Crontab configuration
0 2 * * * /opt/cyber-risk-app/scripts/backup.sh
0 3 * * 0 /opt/cyber-risk-app/scripts/backup_app_state.sh
```

## 🚦 Health Checks & Monitoring

### 1. Service Health Endpoints
```bash
# Application Health
curl https://api.yourdomain.com/health

# Detailed Health Check
curl https://api.yourdomain.com/health/detailed

# Prometheus Metrics
curl https://api.yourdomain.com/metrics

# Performance Report
curl https://api.yourdomain.com/api/monitoring/performance
```

### 2. External Monitoring
```bash
# Uptime monitoring with external service
# Configure monitoring for:
# - https://yourdomain.com (Frontend)
# - https://api.yourdomain.com/health (Backend API)
# - https://monitoring.yourdomain.com (Grafana)
```

## 🔧 Maintenance Procedures

### 1. Rolling Updates
```bash
# Zero-downtime deployment
docker-compose pull
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps frontend
```

### 2. Database Migrations
```bash
# Run migrations
docker-compose exec backend flask db upgrade

# Backup before migration
./scripts/backup.sh
```

### 3. Log Management
```bash
# Log rotation configuration
cat > /etc/logrotate.d/cyber-risk << EOF
/var/lib/docker/containers/*/*-json.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        /bin/kill -USR1 $(cat /var/run/docker.pid) 2>/dev/null || true
    endscript
}
EOF
```

## 📈 Performance Optimization

### 1. Database Optimization
```sql
-- PostgreSQL Performance Tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.7;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

### 2. Redis Configuration
```conf
# redis.conf production settings
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 3. Application Performance
```bash
# Enable application profiling
export PROFILE_ENABLED=true
export PROFILE_THRESHOLD_MS=100

# Configure connection pooling
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=30
```

## 🚨 Troubleshooting Guide

### Common Issues

#### 1. High Memory Usage
```bash
# Check memory usage
docker stats

# Scale down if needed
docker-compose up -d --scale backend=2

# Check for memory leaks
curl https://api.yourdomain.com/api/monitoring/performance?hours=24
```

#### 2. Database Connection Issues
```bash
# Check database connections
docker-compose exec postgres psql -U cyber_user -d cyber_risk_prod -c "SELECT count(*) FROM pg_stat_activity;"

# Restart database if needed
docker-compose restart postgres
```

#### 3. SSL Certificate Issues
```bash
# Check certificate expiry
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/cert.pem -noout -dates

# Force renewal
sudo certbot renew --force-renewal
docker-compose restart nginx
```

## 📞 Support & Maintenance

### Monitoring Contacts
- **Critical Alerts**: ops-team@company.com
- **Performance Issues**: dev-team@company.com
- **Security Issues**: security@company.com

### Escalation Procedures
1. **Level 1**: Service degradation (< 2 hours)
2. **Level 2**: Service outage (< 30 minutes)
3. **Level 3**: Security incident (< 15 minutes)

### Documentation Links
- **Application Docs**: https://docs.yourdomain.com
- **API Reference**: https://api.yourdomain.com/docs
- **Monitoring**: https://monitoring.yourdomain.com
- **GitHub Repository**: https://github.com/Manthanbhanushali010/Stochastic-Cyber-Risk-Simulation-Application

---

## 🎉 Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database initialized and migrated
- [ ] Monitoring stack deployed
- [ ] Backup procedures tested
- [ ] Health checks verified
- [ ] Performance monitoring enabled
- [ ] Security hardening applied
- [ ] Documentation updated
- [ ] Team training completed

**Your enterprise-grade Cyber Risk Simulation Application is now production-ready!** 🚀 