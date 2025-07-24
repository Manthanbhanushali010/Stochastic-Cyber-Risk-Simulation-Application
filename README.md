# Stochastic Cyber Risk Simulation Application

A production-ready platform for stochastic cyber risk event simulation and impact analysis, designed for insurance professionals and risk managers.

## 🎯 Overview

This application provides comprehensive cyber risk modeling capabilities including:
- Monte Carlo simulation of cyber events
- Insurance portfolio impact analysis
- Advanced risk metrics calculation (VaR, TVaR, Expected Loss)
- Interactive dashboard for results visualization
- Scenario analysis and comparison tools

## 🏗️ Architecture

- **Backend**: Flask-based REST API with modular blueprint architecture
- **Frontend**: React with TypeScript for interactive dashboard
- **Database**: SQLAlchemy with PostgreSQL for production
- **Simulation Engine**: NumPy/SciPy-based Monte Carlo simulation
- **Containerization**: Docker for both development and production
- **CI/CD**: GitHub Actions for automated testing and deployment

## 📁 Project Structure

```
├── backend/                 # Flask backend application
│   ├── app/
│   │   ├── models/         # SQLAlchemy database models
│   │   ├── blueprints/     # API endpoints and business logic
│   │   ├── simulation/     # Core simulation engine
│   │   ├── utils/          # Helper utilities
│   │   └── __init__.py     # Flask app factory
│   ├── migrations/         # Database migrations
│   ├── tests/              # Backend tests
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend containerization
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Main application pages
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API integration services
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Frontend utilities
│   ├── public/             # Static assets
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile          # Frontend containerization
├── docker-compose.yml      # Multi-container orchestration
├── .github/workflows/      # CI/CD pipeline configuration
└── docs/                   # Documentation
```

## 🚀 Features

### Core Simulation Capabilities
- **Stochastic Event Generation**: Configurable frequency and severity distributions
- **Portfolio Modeling**: Multi-policy insurance portfolio support
- **Financial Impact Analysis**: Policy terms application (deductibles, limits, reinsurance)
- **Risk Metrics**: VaR, TVaR, Expected Loss calculations
- **Scenario Analysis**: Comparative risk assessment tools

### User Interface
- **Interactive Dashboard**: Real-time simulation results visualization
- **Parameter Input Forms**: Intuitive configuration interface
- **Chart Visualizations**: Loss distributions, scenario comparisons
- **Export Capabilities**: Results export in multiple formats
- **Responsive Design**: Cross-device compatibility

### Technical Features
- **Real-time Updates**: WebSocket-based progress tracking
- **Authentication**: JWT-based user management
- **Performance Optimization**: Vectorized calculations with NumPy
- **Comprehensive Logging**: Structured logging with multiple levels
- **Error Handling**: Robust error management and validation

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.9+ (for local backend development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stochastic-cyber-risk-simulation
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## 📊 Usage

1. **Configure Portfolio**: Define insurance policies with coverage details
2. **Set Event Parameters**: Configure cyber event frequency and severity distributions
3. **Run Simulation**: Execute Monte Carlo simulation with specified iterations
4. **Analyze Results**: View loss distributions, risk metrics, and scenario comparisons
5. **Export Data**: Download results in various formats for further analysis

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Performance

- Optimized for large-scale simulations (100k+ iterations)
- Vectorized calculations using NumPy
- Async processing for long-running simulations
- Caching strategies for repeated calculations

## 🔒 Security

- JWT-based authentication
- Input validation and sanitization
- CORS configuration
- Rate limiting
- Secure headers implementation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or support, please open an issue in the GitHub repository.

---

Built with ❤️ for the cyber risk modeling community 