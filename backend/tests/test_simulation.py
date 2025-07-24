import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.simulation.engine import SimulationEngine
from app.simulation.parameters import SimulationParameters, EventParameters
from app.simulation.distributions import DistributionFactory
from app.simulation.financial import FinancialCalculator, PolicyTerms
from app.simulation.metrics import RiskMetricsCalculator
from app.simulation.exceptions import SimulationError, ParameterValidationError


class TestDistributions:
    """Test distribution classes."""
    
    def test_poisson_distribution(self):
        """Test Poisson distribution implementation."""
        factory = DistributionFactory()
        dist = factory.create_distribution('poisson', {'lambda': 2.5})
        
        # Test mean calculation
        assert abs(dist.mean() - 2.5) < 0.01
        
        # Test variance calculation
        assert abs(dist.variance() - 2.5) < 0.01
        
        # Test sampling
        samples = dist.sample(1000)
        assert len(samples) == 1000
        assert all(isinstance(x, (int, np.integer)) for x in samples)
        assert all(x >= 0 for x in samples)
    
    def test_lognormal_distribution(self):
        """Test Log-Normal distribution implementation."""
        factory = DistributionFactory()
        dist = factory.create_distribution('lognormal', {'mu': 10.0, 'sigma': 1.5})
        
        # Test sampling
        samples = dist.sample(1000)
        assert len(samples) == 1000
        assert all(x > 0 for x in samples)
        
        # Test mean (approximately)
        sample_mean = np.mean(samples)
        theoretical_mean = np.exp(10.0 + (1.5 ** 2) / 2)
        assert abs(sample_mean - theoretical_mean) / theoretical_mean < 0.2
    
    def test_invalid_distribution_type(self):
        """Test creating invalid distribution type."""
        factory = DistributionFactory()
        with pytest.raises(ValueError):
            factory.create_distribution('invalid_distribution', {})
    
    def test_invalid_distribution_parameters(self):
        """Test creating distribution with invalid parameters."""
        factory = DistributionFactory()
        with pytest.raises(ParameterValidationError):
            factory.create_distribution('poisson', {'lambda': -1.0})  # Negative lambda


class TestFinancialCalculator:
    """Test financial calculations."""
    
    def test_simple_loss_calculation(self):
        """Test basic loss calculation without reinsurance."""
        terms = PolicyTerms(
            coverage_amount=1000000,
            deductible=10000,
            policy_limit=1000000
        )
        
        calculator = FinancialCalculator([terms])
        
        # Test loss below deductible
        net_loss = calculator.calculate_single_loss(5000, 0)
        assert net_loss == 0
        
        # Test loss above deductible, below limit
        net_loss = calculator.calculate_single_loss(50000, 0)
        assert net_loss == 40000  # 50000 - 10000 deductible
        
        # Test loss above limit
        net_loss = calculator.calculate_single_loss(1500000, 0)
        assert net_loss == 990000  # limit - deductible
    
    def test_batch_loss_calculation(self):
        """Test batch loss calculations."""
        terms = PolicyTerms(
            coverage_amount=1000000,
            deductible=10000,
            policy_limit=1000000
        )
        
        calculator = FinancialCalculator([terms])
        
        gross_losses = np.array([5000, 50000, 150000, 1500000])
        policy_indices = np.array([0, 0, 0, 0])
        
        net_losses = calculator.calculate_batch_losses(gross_losses, policy_indices)
        expected = np.array([0, 40000, 140000, 990000])
        
        np.testing.assert_array_equal(net_losses, expected)
    
    def test_quota_share_reinsurance(self):
        """Test quota share reinsurance calculation."""
        from app.simulation.financial import ReinsuranceLayer
        
        reinsurance = ReinsuranceLayer(
            layer_type='quota_share',
            parameters={'cession_rate': 0.3}  # 30% quota share
        )
        
        terms = PolicyTerms(
            coverage_amount=1000000,
            deductible=10000,
            policy_limit=1000000,
            reinsurance_layers=[reinsurance]
        )
        
        calculator = FinancialCalculator([terms])
        
        # Test with loss above deductible
        net_loss = calculator.calculate_single_loss(100000, 0)
        # Gross loss: 100000, after deductible: 90000
        # After 30% quota share: 90000 * 0.7 = 63000
        assert net_loss == 63000


class TestRiskMetricsCalculator:
    """Test risk metrics calculations."""
    
    def test_basic_metrics_calculation(self):
        """Test basic risk metrics calculation."""
        losses = np.array([100000, 200000, 300000, 400000, 500000])
        
        calculator = RiskMetricsCalculator()
        metrics = calculator.calculate_metrics(losses)
        
        assert metrics.expected_loss == 300000  # Mean
        assert metrics.max_loss == 500000
        assert metrics.min_loss == 100000
        assert metrics.var_95 == 500000  # 95th percentile
        
        # Test VaR at different confidence levels
        assert 95 in metrics.var_confidence_levels
        assert 99 in metrics.var_confidence_levels
    
    def test_histogram_generation(self):
        """Test histogram data generation."""
        losses = np.random.lognormal(10, 1.5, 10000)
        
        calculator = RiskMetricsCalculator()
        histogram = calculator.generate_histogram(losses, num_bins=20)
        
        assert len(histogram.bins) == 20
        assert len(histogram.frequencies) == 20
        assert sum(histogram.frequencies) <= len(losses)  # Some may be zero
    
    def test_exceedance_curve_generation(self):
        """Test exceedance curve generation."""
        losses = np.array([100, 200, 300, 400, 500])
        
        calculator = RiskMetricsCalculator()
        curve = calculator.generate_exceedance_curve(losses, num_points=5)
        
        assert len(curve.loss_amounts) == 5
        assert len(curve.probabilities) == 5
        assert curve.probabilities[0] == 1.0  # Should start at 1.0
        assert curve.probabilities[-1] == 0.0  # Should end at 0.0


class TestSimulationEngine:
    """Test the main simulation engine."""
    
    def test_engine_initialization(self):
        """Test simulation engine initialization."""
        event_params = EventParameters(
            frequency_distribution='poisson',
            frequency_params={'lambda': 2.5},
            severity_distribution='lognormal',
            severity_params={'mu': 12.0, 'sigma': 1.5}
        )
        
        sim_params = SimulationParameters(
            iterations=1000,
            event_parameters=event_params
        )
        
        engine = SimulationEngine()
        assert engine is not None
    
    @patch('app.simulation.engine.DistributionFactory')
    @patch('app.simulation.engine.FinancialCalculator')
    @patch('app.simulation.engine.RiskMetricsCalculator')
    def test_simulation_run(self, mock_metrics, mock_financial, mock_factory):
        """Test complete simulation run with mocks."""
        # Setup mocks
        mock_freq_dist = MagicMock()
        mock_freq_dist.sample.return_value = np.array([2, 3, 1, 2, 1])
        
        mock_sev_dist = MagicMock()
        mock_sev_dist.sample.return_value = np.array([100000, 200000, 150000])
        
        mock_factory_instance = MagicMock()
        mock_factory_instance.create_distribution.side_effect = [mock_freq_dist, mock_sev_dist]
        mock_factory.return_value = mock_factory_instance
        
        mock_financial_instance = MagicMock()
        mock_financial_instance.calculate_batch_losses.return_value = np.array([80000, 180000, 130000])
        mock_financial.return_value = mock_financial_instance
        
        mock_metrics_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.expected_loss = 150000
        mock_metrics_instance.calculate_metrics.return_value = mock_result
        mock_metrics.return_value = mock_metrics_instance
        
        # Run simulation
        event_params = EventParameters(
            frequency_distribution='poisson',
            frequency_params={'lambda': 2.5},
            severity_distribution='lognormal',
            severity_params={'mu': 12.0, 'sigma': 1.5}
        )
        
        sim_params = SimulationParameters(
            iterations=5,
            event_parameters=event_params
        )
        
        engine = SimulationEngine()
        result = engine.run_simulation(sim_params)
        
        assert result is not None
        assert mock_factory_instance.create_distribution.call_count == 2
        assert mock_financial_instance.calculate_batch_losses.called
        assert mock_metrics_instance.calculate_metrics.called
    
    def test_parameter_validation(self):
        """Test simulation parameter validation."""
        # Test with invalid iterations
        with pytest.raises(ParameterValidationError):
            event_params = EventParameters(
                frequency_distribution='poisson',
                frequency_params={'lambda': 2.5},
                severity_distribution='lognormal',
                severity_params={'mu': 12.0, 'sigma': 1.5}
            )
            
            sim_params = SimulationParameters(
                iterations=-100,  # Invalid
                event_parameters=event_params
            )
            
            sim_params.validate()
    
    def test_progress_callback(self):
        """Test simulation progress callback."""
        progress_updates = []
        
        def progress_callback(progress, message):
            progress_updates.append((progress, message))
        
        event_params = EventParameters(
            frequency_distribution='poisson',
            frequency_params={'lambda': 1.0},
            severity_distribution='lognormal',
            severity_params={'mu': 10.0, 'sigma': 1.0}
        )
        
        sim_params = SimulationParameters(
            iterations=10,
            event_parameters=event_params
        )
        
        engine = SimulationEngine()
        
        # Mock the actual simulation to avoid complexity
        with patch.object(engine, '_run_monte_carlo') as mock_mc:
            mock_mc.return_value = np.array([100000] * 10)
            
            result = engine.run_simulation(sim_params, progress_callback=progress_callback)
            
            # Should have received progress updates
            assert len(progress_updates) > 0
            assert any(progress == 100 for progress, _ in progress_updates)


class TestSimulationAPI:
    """Test simulation API endpoints."""
    
    def test_start_simulation(self, client, auth_headers, test_portfolio):
        """Test starting a new simulation."""
        simulation_data = {
            'name': 'Test Simulation API',
            'portfolio_id': str(test_portfolio.id),
            'iterations': 1000,
            'event_parameters': {
                'frequency_distribution': 'poisson',
                'frequency_params': {'lambda': 2.5},
                'severity_distribution': 'lognormal',
                'severity_params': {'mu': 12.0, 'sigma': 1.5}
            }
        }
        
        response = client.post('/api/simulation/run', 
                             json=simulation_data, 
                             headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'simulation_id' in data
        assert data['status'] == 'running'
    
    def test_get_simulation_list(self, client, auth_headers, test_simulation_run):
        """Test getting list of user simulations."""
        response = client.get('/api/simulation/list', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'simulations' in data
        assert len(data['simulations']) >= 1
    
    def test_get_simulation_details(self, client, auth_headers, test_simulation_run):
        """Test getting simulation details."""
        response = client.get(f'/api/simulation/{test_simulation_run.id}', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == str(test_simulation_run.id)
        assert data['name'] == 'Test Simulation'
    
    def test_get_simulation_unauthorized(self, client, auth_headers):
        """Test getting simulation without proper authorization."""
        # Try to access non-existent simulation
        response = client.get('/api/simulation/999', headers=auth_headers)
        assert response.status_code == 404 