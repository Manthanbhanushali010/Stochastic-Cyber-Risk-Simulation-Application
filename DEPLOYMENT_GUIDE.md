# Stochastic Cyber Risk Simulation Application - Deployment Guide

## Overview

This is a production-ready **Stochastic Cyber Risk Simulation Application** that provides Monte Carlo simulations for cyber risk assessment with a modern React frontend and Flask backend.

## 🏗️ Architecture

- **Frontend**: React 18 with TypeScript, Zustand for state management, Chart.js and Plotly for visualizations
- **Backend**: Flask with SQLAlchemy, JWT authentication, WebSocket support
- **Database**: PostgreSQL 15 for data persistence
- **Cache**: Redis for session management and real-time features
- **Simulation Engine**: Custom Monte Carlo engine with multiple probability distributions
- **Containerization**: Docker and Docker Compose for easy deployment

## 📋 Prerequisites

Before deploying the application, ensure you have:

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** for cloning the repository
- **Node.js 18+** (for local frontend development)
- **Python 3.11+** (for local backend development)

## 🚀 Quick Start (Docker Deployment)

### 1. Clone and Prepare

```bash
# Clone the repository
git clone <repository-url>
cd "Stochastic Cyber Risk Simulation Application"

# Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Configure Environment

Edit `backend/.env`:
```env
FLASK_ENV=docker
DATABASE_URL=postgresql://postgres:password@db:5432/cyber_risk
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
```

Edit `frontend/.env`:
```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WS_URL=ws://localhost:5000
```

### 3. Deploy with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **API Documentation**: http://localhost:5000/api/docs (if implemented)

## 🛠️ Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your local database settings

# Initialize database
flask db init
flask db migrate -m "Initial migration" 
flask db upgrade

# Run development server
python app.py
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## 🔧 Configuration

### Backend Configuration

The backend uses environment-based configuration:

- **`config.py`**: Main configuration file with classes for different environments
- **Environment variables**: Override configuration through `.env` file
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh token support
- **CORS**: Configured for frontend communication

### Frontend Configuration

- **Environment variables**: Set API URLs and feature flags
- **Theme**: Centralized theme configuration in `App.tsx`
- **State management**: Zustand stores for auth, UI, and application state
- **Routing**: React Router with protected routes

### Simulation Engine Configuration

Key parameters for Monte Carlo simulations:

- **Frequency Distributions**: Poisson, Negative Binomial, Binomial
- **Severity Distributions**: LogNormal, Pareto, Gamma, Exponential, Weibull
- **Risk Metrics**: VaR, TVaR, Expected Loss, distribution statistics
- **Financial Calculations**: Deductibles, limits, reinsurance modeling

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run unit tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov-report=html

# Test specific module
python -m pytest tests/test_simulation.py -v
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in CI mode
npm test -- --ci --coverage --watchAll=false
```

## 📊 API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/refresh` - Refresh access token

### Simulation Endpoints

- `POST /api/simulation/run` - Start new simulation
- `GET /api/simulation/list` - List user simulations
- `GET /api/simulation/{id}` - Get simulation details
- `GET /api/simulation/{id}/results` - Get simulation results
- `POST /api/simulation/{id}/stop` - Stop running simulation
- `DELETE /api/simulation/{id}` - Delete simulation

### Portfolio Endpoints

- `POST /api/portfolio/` - Create portfolio
- `GET /api/portfolio/` - List portfolios
- `GET /api/portfolio/{id}` - Get portfolio details
- `PUT /api/portfolio/{id}` - Update portfolio
- `DELETE /api/portfolio/{id}` - Delete portfolio
- `POST /api/portfolio/{id}/policies` - Add policy to portfolio

### Scenario Endpoints

- `POST /api/scenarios/` - Create scenario
- `GET /api/scenarios/` - List scenarios
- `GET /api/scenarios/{id}` - Get scenario details
- `PUT /api/scenarios/{id}` - Update scenario
- `POST /api/scenarios/compare` - Compare multiple scenarios

## 🔒 Security Features

### Authentication & Authorization

- **JWT Tokens**: Access and refresh token system
- **Password Hashing**: Bcrypt with salt rounds
- **CORS Protection**: Configured allowed origins
- **Input Validation**: Marshmallow schemas for API validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

### Infrastructure Security

- **Docker Security**: Non-root user, minimal base images
- **Environment Variables**: Secrets management through environment files
- **HTTPS Support**: Nginx configuration for SSL/TLS
- **Security Headers**: CSP, HSTS, X-Frame-Options configured

## 📈 Performance Optimization

### Backend Performance

- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: SQLAlchemy connection pool configuration
- **Caching**: Redis for session and frequently accessed data
- **Parallel Processing**: Multiprocessing for Monte Carlo simulations
- **Async Operations**: WebSocket for real-time simulation updates

### Frontend Performance

- **Code Splitting**: Dynamic imports for route-based splitting
- **Memoization**: React optimization with useMemo and useCallback
- **Virtual Scrolling**: For large data sets in tables and lists
- **Chart Optimization**: Efficient data visualization with Chart.js
- **Bundle Optimization**: Webpack optimization for production builds

## 🚀 Production Deployment

### Environment Preparation

1. **Server Setup**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **SSL Certificate** (Let's Encrypt):
   ```bash
   # Install Certbot
   sudo apt install certbot
   
   # Generate certificate
   sudo certbot certonly --standalone -d yourdomain.com
   ```

3. **Production Environment**:
   ```bash
   # Set production environment variables
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@prod-db:5432/cyber_risk
   
   # Deploy with production profile
   docker-compose --profile production up -d
   ```

### Nginx Configuration

Create production Nginx configuration in `nginx/nginx.conf`:

```nginx
upstream backend {
    server backend:5000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/ssl/fullchain.pem;
    ssl_certificate_key /etc/ssl/privkey.pem;
    
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /socket.io {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 📝 Usage Guide

### 1. User Registration and Login

1. Navigate to http://localhost:3000
2. Click "Register" to create a new account
3. Fill in email, username, and password
4. Login with your credentials

### 2. Creating a Portfolio

1. Go to "Portfolio" section
2. Click "Create New Portfolio"
3. Add policies with coverage details:
   - Policy number and holder information
   - Coverage limits and deductibles
   - Industry sector and risk attributes

### 3. Running Simulations

1. Navigate to "Simulation" page
2. Configure simulation parameters:
   - **Frequency Distribution**: Choose from Poisson, Negative Binomial, or Binomial
   - **Severity Distribution**: Select LogNormal, Pareto, Gamma, Exponential, or Weibull
   - **Number of Iterations**: Typically 10,000 - 100,000 for stable results
   - **Risk Parameters**: Set distribution parameters based on historical data

3. Advanced Settings:
   - Enable correlation between frequency and severity
   - Configure deductibles and coverage limits
   - Set up reinsurance arrangements
   - Choose parallel processing options

4. Click "Run Simulation" and monitor progress via real-time updates

### 4. Analyzing Results

The results dashboard provides:

- **Risk Metrics**: VaR at 95%, 99%, and 99.9% confidence levels
- **Distribution Charts**: Histogram of loss distribution
- **Exceedance Curves**: Probability of exceeding loss thresholds
- **Statistical Measures**: Expected loss, standard deviation, skewness, kurtosis

### 5. Scenario Analysis

1. Create scenarios with modified parameters
2. Compare baseline vs. stressed scenarios
3. Analyze impact of parameter changes
4. Export results for reporting

## 🔍 Monitoring and Logging

### Application Monitoring

```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Monitor resource usage
docker stats

# Check health status
curl http://localhost:5000/api/health
curl http://localhost:3000/health
```

### Database Monitoring

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d cyber_risk

# Check database size
SELECT pg_size_pretty(pg_database_size('cyber_risk'));

# Monitor active connections
SELECT count(*) FROM pg_stat_activity;
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```bash
   # Check what's using port 5000
   lsof -i :5000
   # Kill process or change port in docker-compose.yml
   ```

2. **Database Connection Issues**:
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up -d db
   # Wait for db to be ready, then start other services
   ```

3. **Frontend Build Issues**:
   ```bash
   # Clear node modules and rebuild
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

4. **Memory Issues with Simulations**:
   - Reduce number of iterations
   - Enable batch processing
   - Adjust Docker memory limits

### Performance Tuning

1. **Database Performance**:
   ```sql
   -- Add indexes for common queries
   CREATE INDEX idx_simulation_runs_user_id ON simulation_runs(user_id);
   CREATE INDEX idx_simulation_runs_status ON simulation_runs(status);
   ```

2. **Redis Configuration**:
   ```bash
   # Increase Redis memory limit
   docker-compose exec redis redis-cli CONFIG SET maxmemory 512mb
   ```

## 📚 Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **React Documentation**: https://reactjs.org/docs/
- **Docker Documentation**: https://docs.docker.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Monte Carlo Methods**: Academic papers and risk management resources

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Commit with descriptive messages
5. Push to branch and create pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check this deployment guide
2. Review application logs
3. Check GitHub issues
4. Create new issue with detailed information

---

**🎉 Your Stochastic Cyber Risk Simulation Application is now ready for production use!** 