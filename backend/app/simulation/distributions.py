"""
Probability distribution classes for cyber risk simulation.

This module provides frequency and severity distribution implementations
for Monte Carlo simulation of cyber events.
"""

import numpy as np
from scipy import stats
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from .exceptions import DistributionError


class Distribution(ABC):
    """Abstract base class for probability distributions."""
    
    def __init__(self, params: Dict[str, float]):
        """Initialize distribution with parameters."""
        self.params = params
        self.validate_params()
    
    @abstractmethod
    def validate_params(self) -> None:
        """Validate distribution parameters."""
        pass
    
    @abstractmethod
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate random samples from the distribution."""
        pass
    
    @abstractmethod
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Probability density function."""
        pass
    
    @abstractmethod
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Cumulative distribution function."""
        pass
    
    @abstractmethod
    def mean(self) -> float:
        """Calculate distribution mean."""
        pass
    
    @abstractmethod
    def variance(self) -> float:
        """Calculate distribution variance."""
        pass


class FrequencyDistribution(Distribution):
    """Base class for frequency distributions (discrete)."""
    
    @abstractmethod
    def pmf(self, k: Union[int, np.ndarray]) -> Union[float, np.ndarray]:
        """Probability mass function."""
        pass


class SeverityDistribution(Distribution):
    """Base class for severity distributions (continuous)."""
    
    @abstractmethod
    def ppf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Percent point function (inverse CDF)."""
        pass


# Frequency Distributions

class PoissonDistribution(FrequencyDistribution):
    """Poisson distribution for event frequency."""
    
    def validate_params(self) -> None:
        """Validate Poisson parameters."""
        if 'lambda' not in self.params:
            raise DistributionError("Poisson distribution requires 'lambda' parameter")
        if self.params['lambda'] <= 0:
            raise DistributionError("Poisson lambda must be positive")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate Poisson random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return random_state.poisson(self.params['lambda'], size)
    
    def pmf(self, k: Union[int, np.ndarray]) -> Union[float, np.ndarray]:
        """Poisson probability mass function."""
        return stats.poisson.pmf(k, self.params['lambda'])
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """For discrete distributions, PDF equals PMF."""
        return self.pmf(x)
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Poisson cumulative distribution function."""
        return stats.poisson.cdf(x, self.params['lambda'])
    
    def mean(self) -> float:
        """Poisson mean."""
        return self.params['lambda']
    
    def variance(self) -> float:
        """Poisson variance."""
        return self.params['lambda']


class NegativeBinomialDistribution(FrequencyDistribution):
    """Negative binomial distribution for event frequency."""
    
    def validate_params(self) -> None:
        """Validate negative binomial parameters."""
        required_params = ['n', 'p']
        for param in required_params:
            if param not in self.params:
                raise DistributionError(f"Negative binomial distribution requires '{param}' parameter")
        if self.params['n'] <= 0:
            raise DistributionError("Negative binomial n must be positive")
        if not 0 < self.params['p'] <= 1:
            raise DistributionError("Negative binomial p must be between 0 and 1")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate negative binomial random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return random_state.negative_binomial(self.params['n'], self.params['p'], size)
    
    def pmf(self, k: Union[int, np.ndarray]) -> Union[float, np.ndarray]:
        """Negative binomial probability mass function."""
        return stats.nbinom.pmf(k, self.params['n'], self.params['p'])
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """For discrete distributions, PDF equals PMF."""
        return self.pmf(x)
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Negative binomial cumulative distribution function."""
        return stats.nbinom.cdf(x, self.params['n'], self.params['p'])
    
    def mean(self) -> float:
        """Negative binomial mean."""
        return self.params['n'] * (1 - self.params['p']) / self.params['p']
    
    def variance(self) -> float:
        """Negative binomial variance."""
        return self.params['n'] * (1 - self.params['p']) / (self.params['p'] ** 2)


class BinomialDistribution(FrequencyDistribution):
    """Binomial distribution for event frequency."""
    
    def validate_params(self) -> None:
        """Validate binomial parameters."""
        required_params = ['n', 'p']
        for param in required_params:
            if param not in self.params:
                raise DistributionError(f"Binomial distribution requires '{param}' parameter")
        if self.params['n'] <= 0 or not isinstance(self.params['n'], (int, float)) or self.params['n'] != int(self.params['n']):
            raise DistributionError("Binomial n must be a positive integer")
        if not 0 <= self.params['p'] <= 1:
            raise DistributionError("Binomial p must be between 0 and 1")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate binomial random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return random_state.binomial(int(self.params['n']), self.params['p'], size)
    
    def pmf(self, k: Union[int, np.ndarray]) -> Union[float, np.ndarray]:
        """Binomial probability mass function."""
        return stats.binom.pmf(k, int(self.params['n']), self.params['p'])
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """For discrete distributions, PDF equals PMF."""
        return self.pmf(x)
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Binomial cumulative distribution function."""
        return stats.binom.cdf(x, int(self.params['n']), self.params['p'])
    
    def mean(self) -> float:
        """Binomial mean."""
        return self.params['n'] * self.params['p']
    
    def variance(self) -> float:
        """Binomial variance."""
        return self.params['n'] * self.params['p'] * (1 - self.params['p'])


# Severity Distributions

class LogNormalDistribution(SeverityDistribution):
    """Log-normal distribution for event severity."""
    
    def validate_params(self) -> None:
        """Validate log-normal parameters."""
        required_params = ['mu', 'sigma']
        for param in required_params:
            if param not in self.params:
                raise DistributionError(f"Log-normal distribution requires '{param}' parameter")
        if self.params['sigma'] <= 0:
            raise DistributionError("Log-normal sigma must be positive")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate log-normal random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return random_state.lognormal(self.params['mu'], self.params['sigma'], size)
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Log-normal probability density function."""
        return stats.lognorm.pdf(x, s=self.params['sigma'], scale=np.exp(self.params['mu']))
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Log-normal cumulative distribution function."""
        return stats.lognorm.cdf(x, s=self.params['sigma'], scale=np.exp(self.params['mu']))
    
    def ppf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Log-normal percent point function."""
        return stats.lognorm.ppf(q, s=self.params['sigma'], scale=np.exp(self.params['mu']))
    
    def mean(self) -> float:
        """Log-normal mean."""
        return np.exp(self.params['mu'] + 0.5 * self.params['sigma'] ** 2)
    
    def variance(self) -> float:
        """Log-normal variance."""
        exp_2mu_sigma2 = np.exp(2 * self.params['mu'] + self.params['sigma'] ** 2)
        return exp_2mu_sigma2 * (np.exp(self.params['sigma'] ** 2) - 1)


class ParetoDistribution(SeverityDistribution):
    """Pareto distribution for event severity."""
    
    def validate_params(self) -> None:
        """Validate Pareto parameters."""
        required_params = ['scale', 'shape']
        for param in required_params:
            if param not in self.params:
                raise DistributionError(f"Pareto distribution requires '{param}' parameter")
        if self.params['scale'] <= 0 or self.params['shape'] <= 0:
            raise DistributionError("Pareto scale and shape must be positive")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate Pareto random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return random_state.pareto(self.params['shape'], size) * self.params['scale'] + self.params['scale']
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Pareto probability density function."""
        return stats.pareto.pdf(x, self.params['shape'], scale=self.params['scale'])
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Pareto cumulative distribution function."""
        return stats.pareto.cdf(x, self.params['shape'], scale=self.params['scale'])
    
    def ppf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Pareto percent point function."""
        return stats.pareto.ppf(q, self.params['shape'], scale=self.params['scale'])
    
    def mean(self) -> float:
        """Pareto mean."""
        if self.params['shape'] <= 1:
            return np.inf
        return self.params['shape'] * self.params['scale'] / (self.params['shape'] - 1)
    
    def variance(self) -> float:
        """Pareto variance."""
        if self.params['shape'] <= 2:
            return np.inf
        shape = self.params['shape']
        scale = self.params['scale']
        return (scale ** 2 * shape) / ((shape - 1) ** 2 * (shape - 2))


class GammaDistribution(SeverityDistribution):
    """Gamma distribution for event severity."""
    
    def validate_params(self) -> None:
        """Validate Gamma parameters."""
        required_params = ['shape', 'scale']
        for param in required_params:
            if param not in self.params:
                raise DistributionError(f"Gamma distribution requires '{param}' parameter")
        if self.params['shape'] <= 0 or self.params['scale'] <= 0:
            raise DistributionError("Gamma shape and scale must be positive")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate Gamma random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return random_state.gamma(self.params['shape'], self.params['scale'], size)
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Gamma probability density function."""
        return stats.gamma.pdf(x, self.params['shape'], scale=self.params['scale'])
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Gamma cumulative distribution function."""
        return stats.gamma.cdf(x, self.params['shape'], scale=self.params['scale'])
    
    def ppf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Gamma percent point function."""
        return stats.gamma.ppf(q, self.params['shape'], scale=self.params['scale'])
    
    def mean(self) -> float:
        """Gamma mean."""
        return self.params['shape'] * self.params['scale']
    
    def variance(self) -> float:
        """Gamma variance."""
        return self.params['shape'] * (self.params['scale'] ** 2)


class ExponentialDistribution(SeverityDistribution):
    """Exponential distribution for event severity."""
    
    def validate_params(self) -> None:
        """Validate Exponential parameters."""
        if 'scale' not in self.params:
            raise DistributionError("Exponential distribution requires 'scale' parameter")
        if self.params['scale'] <= 0:
            raise DistributionError("Exponential scale must be positive")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate Exponential random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return random_state.exponential(self.params['scale'], size)
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Exponential probability density function."""
        return stats.expon.pdf(x, scale=self.params['scale'])
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Exponential cumulative distribution function."""
        return stats.expon.cdf(x, scale=self.params['scale'])
    
    def ppf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Exponential percent point function."""
        return stats.expon.ppf(q, scale=self.params['scale'])
    
    def mean(self) -> float:
        """Exponential mean."""
        return self.params['scale']
    
    def variance(self) -> float:
        """Exponential variance."""
        return self.params['scale'] ** 2


class WeibullDistribution(SeverityDistribution):
    """Weibull distribution for event severity."""
    
    def validate_params(self) -> None:
        """Validate Weibull parameters."""
        required_params = ['shape', 'scale']
        for param in required_params:
            if param not in self.params:
                raise DistributionError(f"Weibull distribution requires '{param}' parameter")
        if self.params['shape'] <= 0 or self.params['scale'] <= 0:
            raise DistributionError("Weibull shape and scale must be positive")
    
    def sample(self, size: int, random_state: Optional[np.random.RandomState] = None) -> np.ndarray:
        """Generate Weibull random samples."""
        if random_state is None:
            random_state = np.random.RandomState()
        return self.params['scale'] * random_state.weibull(self.params['shape'], size)
    
    def pdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Weibull probability density function."""
        return stats.weibull_min.pdf(x, self.params['shape'], scale=self.params['scale'])
    
    def cdf(self, x: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Weibull cumulative distribution function."""
        return stats.weibull_min.cdf(x, self.params['shape'], scale=self.params['scale'])
    
    def ppf(self, q: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
        """Weibull percent point function."""
        return stats.weibull_min.ppf(q, self.params['shape'], scale=self.params['scale'])
    
    def mean(self) -> float:
        """Weibull mean."""
        from scipy.special import gamma
        return self.params['scale'] * gamma(1 + 1/self.params['shape'])
    
    def variance(self) -> float:
        """Weibull variance."""
        from scipy.special import gamma
        scale = self.params['scale']
        shape = self.params['shape']
        return scale**2 * (gamma(1 + 2/shape) - (gamma(1 + 1/shape))**2)


class DistributionFactory:
    """Factory class for creating distribution instances."""
    
    FREQUENCY_DISTRIBUTIONS = {
        'poisson': PoissonDistribution,
        'negative_binomial': NegativeBinomialDistribution,
        'binomial': BinomialDistribution
    }
    
    SEVERITY_DISTRIBUTIONS = {
        'lognormal': LogNormalDistribution,
        'pareto': ParetoDistribution,
        'gamma': GammaDistribution,
        'exponential': ExponentialDistribution,
        'weibull': WeibullDistribution
    }
    
    @classmethod
    def create_frequency_distribution(cls, distribution_name: str, params: Dict[str, float]) -> FrequencyDistribution:
        """Create a frequency distribution instance."""
        if distribution_name not in cls.FREQUENCY_DISTRIBUTIONS:
            raise DistributionError(
                f"Unknown frequency distribution: {distribution_name}",
                {'available_distributions': list(cls.FREQUENCY_DISTRIBUTIONS.keys())}
            )
        
        distribution_class = cls.FREQUENCY_DISTRIBUTIONS[distribution_name]
        return distribution_class(params)
    
    @classmethod
    def create_severity_distribution(cls, distribution_name: str, params: Dict[str, float]) -> SeverityDistribution:
        """Create a severity distribution instance."""
        if distribution_name not in cls.SEVERITY_DISTRIBUTIONS:
            raise DistributionError(
                f"Unknown severity distribution: {distribution_name}",
                {'available_distributions': list(cls.SEVERITY_DISTRIBUTIONS.keys())}
            )
        
        distribution_class = cls.SEVERITY_DISTRIBUTIONS[distribution_name]
        return distribution_class(params)
    
    @classmethod
    def get_available_distributions(cls) -> Dict[str, list]:
        """Get lists of available distributions."""
        return {
            'frequency': list(cls.FREQUENCY_DISTRIBUTIONS.keys()),
            'severity': list(cls.SEVERITY_DISTRIBUTIONS.keys())
        } 