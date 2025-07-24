"""
Parameter classes for simulation configuration and validation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from .exceptions import ParameterError, ValidationError


@dataclass
class EventParameters:
    """Parameters for cyber event modeling."""
    
    # Frequency distribution parameters
    frequency_distribution: str = 'poisson'
    frequency_params: Dict[str, float] = field(default_factory=dict)
    
    # Severity distribution parameters
    severity_distribution: str = 'lognormal'
    severity_params: Dict[str, float] = field(default_factory=dict)
    
    # Event correlation parameters
    correlation_enabled: bool = False
    correlation_params: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> None:
        """Validate event parameters."""
        self._validate_frequency_params()
        self._validate_severity_params()
        self._validate_correlation_params()
    
    def _validate_frequency_params(self) -> None:
        """Validate frequency distribution parameters."""
        valid_distributions = ['poisson', 'negative_binomial', 'binomial']
        
        if self.frequency_distribution not in valid_distributions:
            raise ParameterError(
                f"Invalid frequency distribution: {self.frequency_distribution}",
                {'valid_distributions': valid_distributions}
            )
        
        if self.frequency_distribution == 'poisson':
            if 'lambda' not in self.frequency_params:
                raise ParameterError("Poisson distribution requires 'lambda' parameter")
            if self.frequency_params['lambda'] <= 0:
                raise ParameterError("Poisson lambda must be positive")
        
        elif self.frequency_distribution == 'negative_binomial':
            required_params = ['n', 'p']
            for param in required_params:
                if param not in self.frequency_params:
                    raise ParameterError(f"Negative binomial distribution requires '{param}' parameter")
            if self.frequency_params['n'] <= 0:
                raise ParameterError("Negative binomial n must be positive")
            if not 0 < self.frequency_params['p'] <= 1:
                raise ParameterError("Negative binomial p must be between 0 and 1")
        
        elif self.frequency_distribution == 'binomial':
            required_params = ['n', 'p']
            for param in required_params:
                if param not in self.frequency_params:
                    raise ParameterError(f"Binomial distribution requires '{param}' parameter")
            if self.frequency_params['n'] <= 0 or not isinstance(self.frequency_params['n'], int):
                raise ParameterError("Binomial n must be a positive integer")
            if not 0 <= self.frequency_params['p'] <= 1:
                raise ParameterError("Binomial p must be between 0 and 1")
    
    def _validate_severity_params(self) -> None:
        """Validate severity distribution parameters."""
        valid_distributions = ['lognormal', 'pareto', 'gamma', 'exponential', 'weibull']
        
        if self.severity_distribution not in valid_distributions:
            raise ParameterError(
                f"Invalid severity distribution: {self.severity_distribution}",
                {'valid_distributions': valid_distributions}
            )
        
        if self.severity_distribution == 'lognormal':
            required_params = ['mu', 'sigma']
            for param in required_params:
                if param not in self.severity_params:
                    raise ParameterError(f"Lognormal distribution requires '{param}' parameter")
            if self.severity_params['sigma'] <= 0:
                raise ParameterError("Lognormal sigma must be positive")
        
        elif self.severity_distribution == 'pareto':
            required_params = ['scale', 'shape']
            for param in required_params:
                if param not in self.severity_params:
                    raise ParameterError(f"Pareto distribution requires '{param}' parameter")
            if self.severity_params['scale'] <= 0 or self.severity_params['shape'] <= 0:
                raise ParameterError("Pareto scale and shape must be positive")
        
        elif self.severity_distribution == 'gamma':
            required_params = ['shape', 'scale']
            for param in required_params:
                if param not in self.severity_params:
                    raise ParameterError(f"Gamma distribution requires '{param}' parameter")
            if self.severity_params['shape'] <= 0 or self.severity_params['scale'] <= 0:
                raise ParameterError("Gamma shape and scale must be positive")
        
        elif self.severity_distribution == 'exponential':
            if 'scale' not in self.severity_params:
                raise ParameterError("Exponential distribution requires 'scale' parameter")
            if self.severity_params['scale'] <= 0:
                raise ParameterError("Exponential scale must be positive")
        
        elif self.severity_distribution == 'weibull':
            required_params = ['shape', 'scale']
            for param in required_params:
                if param not in self.severity_params:
                    raise ParameterError(f"Weibull distribution requires '{param}' parameter")
            if self.severity_params['shape'] <= 0 or self.severity_params['scale'] <= 0:
                raise ParameterError("Weibull shape and scale must be positive")
    
    def _validate_correlation_params(self) -> None:
        """Validate correlation parameters."""
        if self.correlation_enabled and not self.correlation_params:
            raise ParameterError("Correlation enabled but no correlation parameters provided")


@dataclass
class SimulationParameters:
    """Main simulation configuration parameters."""
    
    # Basic simulation settings
    num_iterations: int = 10000
    random_seed: Optional[int] = None
    
    # Event parameters
    event_params: EventParameters = field(default_factory=EventParameters)
    
    # Portfolio parameters
    portfolio_id: Optional[str] = None
    portfolio_config: Dict[str, Any] = field(default_factory=dict)
    
    # Financial calculation parameters
    apply_deductibles: bool = True
    apply_limits: bool = True
    apply_reinsurance: bool = False
    reinsurance_config: Dict[str, Any] = field(default_factory=dict)
    
    # Simulation control parameters
    max_events_per_iteration: int = 100
    convergence_check: bool = False
    convergence_threshold: float = 0.001
    convergence_window: int = 1000
    
    # Performance parameters
    batch_size: int = 1000
    parallel_processing: bool = True
    max_workers: Optional[int] = None
    
    # Output parameters
    save_raw_losses: bool = False
    calculate_percentiles: bool = True
    percentile_levels: List[float] = field(default_factory=lambda: [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999])
    
    def validate(self) -> None:
        """Validate all simulation parameters."""
        self._validate_basic_params()
        self._validate_event_params()
        self._validate_portfolio_params()
        self._validate_financial_params()
        self._validate_performance_params()
        self._validate_output_params()
    
    def _validate_basic_params(self) -> None:
        """Validate basic simulation parameters."""
        if self.num_iterations <= 0:
            raise ParameterError("Number of iterations must be positive")
        
        if self.num_iterations > 10_000_000:
            raise ParameterError("Number of iterations exceeds maximum limit (10M)")
        
        if self.random_seed is not None and (self.random_seed < 0 or self.random_seed > 2**32 - 1):
            raise ParameterError("Random seed must be between 0 and 2^32-1")
    
    def _validate_event_params(self) -> None:
        """Validate event parameters."""
        try:
            self.event_params.validate()
        except (ParameterError, ValidationError) as e:
            raise ParameterError(f"Event parameter validation failed: {e.message}")
    
    def _validate_portfolio_params(self) -> None:
        """Validate portfolio parameters."""
        # Portfolio validation will be handled by the portfolio service
        pass
    
    def _validate_financial_params(self) -> None:
        """Validate financial calculation parameters."""
        if self.apply_reinsurance and not self.reinsurance_config:
            raise ParameterError("Reinsurance enabled but no configuration provided")
        
        if self.max_events_per_iteration <= 0:
            raise ParameterError("Max events per iteration must be positive")
        
        if self.max_events_per_iteration > 10000:
            raise ParameterError("Max events per iteration exceeds reasonable limit")
    
    def _validate_performance_params(self) -> None:
        """Validate performance parameters."""
        if self.batch_size <= 0:
            raise ParameterError("Batch size must be positive")
        
        if self.batch_size > self.num_iterations:
            raise ParameterError("Batch size cannot exceed number of iterations")
        
        if self.max_workers is not None and self.max_workers <= 0:
            raise ParameterError("Max workers must be positive")
        
        if self.convergence_check:
            if self.convergence_threshold <= 0:
                raise ParameterError("Convergence threshold must be positive")
            if self.convergence_window <= 0:
                raise ParameterError("Convergence window must be positive")
            if self.convergence_window >= self.num_iterations:
                raise ParameterError("Convergence window must be less than total iterations")
    
    def _validate_output_params(self) -> None:
        """Validate output parameters."""
        if self.calculate_percentiles:
            for percentile in self.percentile_levels:
                if not 0 <= percentile <= 1:
                    raise ParameterError(f"Percentile {percentile} must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert parameters to dictionary representation."""
        return {
            'num_iterations': self.num_iterations,
            'random_seed': self.random_seed,
            'event_params': {
                'frequency_distribution': self.event_params.frequency_distribution,
                'frequency_params': self.event_params.frequency_params,
                'severity_distribution': self.event_params.severity_distribution,
                'severity_params': self.event_params.severity_params,
                'correlation_enabled': self.event_params.correlation_enabled,
                'correlation_params': self.event_params.correlation_params
            },
            'portfolio_id': self.portfolio_id,
            'portfolio_config': self.portfolio_config,
            'apply_deductibles': self.apply_deductibles,
            'apply_limits': self.apply_limits,
            'apply_reinsurance': self.apply_reinsurance,
            'reinsurance_config': self.reinsurance_config,
            'max_events_per_iteration': self.max_events_per_iteration,
            'convergence_check': self.convergence_check,
            'convergence_threshold': self.convergence_threshold,
            'convergence_window': self.convergence_window,
            'batch_size': self.batch_size,
            'parallel_processing': self.parallel_processing,
            'max_workers': self.max_workers,
            'save_raw_losses': self.save_raw_losses,
            'calculate_percentiles': self.calculate_percentiles,
            'percentile_levels': self.percentile_levels
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationParameters':
        """Create parameters from dictionary."""
        event_params_data = data.get('event_params', {})
        event_params = EventParameters(
            frequency_distribution=event_params_data.get('frequency_distribution', 'poisson'),
            frequency_params=event_params_data.get('frequency_params', {}),
            severity_distribution=event_params_data.get('severity_distribution', 'lognormal'),
            severity_params=event_params_data.get('severity_params', {}),
            correlation_enabled=event_params_data.get('correlation_enabled', False),
            correlation_params=event_params_data.get('correlation_params', {})
        )
        
        return cls(
            num_iterations=data.get('num_iterations', 10000),
            random_seed=data.get('random_seed'),
            event_params=event_params,
            portfolio_id=data.get('portfolio_id'),
            portfolio_config=data.get('portfolio_config', {}),
            apply_deductibles=data.get('apply_deductibles', True),
            apply_limits=data.get('apply_limits', True),
            apply_reinsurance=data.get('apply_reinsurance', False),
            reinsurance_config=data.get('reinsurance_config', {}),
            max_events_per_iteration=data.get('max_events_per_iteration', 100),
            convergence_check=data.get('convergence_check', False),
            convergence_threshold=data.get('convergence_threshold', 0.001),
            convergence_window=data.get('convergence_window', 1000),
            batch_size=data.get('batch_size', 1000),
            parallel_processing=data.get('parallel_processing', True),
            max_workers=data.get('max_workers'),
            save_raw_losses=data.get('save_raw_losses', False),
            calculate_percentiles=data.get('calculate_percentiles', True),
            percentile_levels=data.get('percentile_levels', [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999])
        ) 