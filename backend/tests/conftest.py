import pytest
import tempfile
import os
from app import create_app, db
from app.models import User, Portfolio, Policy, SimulationRun


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to serve as the database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Authentication headers for API requests."""
    # Register and login a test user
    user_data = {
        'email': 'test@example.com',
        'username': 'testuser',
        'password': 'testpassword123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    client.post('/api/auth/register', json=user_data)
    
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword123'
    }
    
    response = client.post('/api/auth/login', json=login_data)
    token = response.get_json()['access_token']
    
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_portfolio(app, test_user):
    """Create a test portfolio with policies."""
    with app.app_context():
        portfolio = Portfolio(
            name='Test Portfolio',
            description='A test portfolio for unit tests',
            user_id=test_user.id
        )
        db.session.add(portfolio)
        db.session.flush()
        
        # Add test policies
        policies = [
            Policy(
                name='Policy 1',
                coverage_amount=1000000,
                deductible=10000,
                policy_limit=1000000,
                industry='Technology',
                portfolio_id=portfolio.id
            ),
            Policy(
                name='Policy 2',
                coverage_amount=500000,
                deductible=5000,
                policy_limit=500000,
                industry='Healthcare',
                portfolio_id=portfolio.id
            )
        ]
        
        for policy in policies:
            db.session.add(policy)
        
        db.session.commit()
        return portfolio


@pytest.fixture
def test_simulation_run(app, test_user, test_portfolio):
    """Create a test simulation run."""
    with app.app_context():
        simulation = SimulationRun(
            name='Test Simulation',
            user_id=test_user.id,
            portfolio_id=test_portfolio.id,
            iterations=1000,
            parameters={
                'frequency_distribution': 'poisson',
                'frequency_params': {'lambda': 2.5},
                'severity_distribution': 'lognormal',
                'severity_params': {'mu': 12.5, 'sigma': 1.8}
            },
            status='completed'
        )
        db.session.add(simulation)
        db.session.commit()
        return simulation 