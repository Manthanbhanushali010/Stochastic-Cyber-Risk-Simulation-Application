"""
Risk metrics calculation module for cyber risk simulation.

This module provides comprehensive risk metrics calculation including
VaR, TVaR, Expected Loss, and various distribution statistics.
"""

import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from .exceptions import SimulationError


@dataclass
class RiskMetrics:
    """Container for calculated risk metrics."""
    
    # Basic statistics
    expected_loss: float
    standard_deviation: float
    variance: float
    minimum_loss: float
    maximum_loss: float
    
    # Risk measures
    var_95: float
    var_99: float
    var_99_9: float
    tvar_95: float
    tvar_99: float
    tvar_99_9: float
    
    # Distribution properties
    skewness: float
    kurtosis: float
    coefficient_of_variation: float
    
    # Additional metrics
    probability_of_loss: float
    median_loss: float
    mode_loss: Optional[float] = None
    
    # Percentiles
    percentiles: Optional[Dict[str, float]] = None
    
    # Distribution data for visualization
    histogram_data: Optional[Dict[str, Any]] = None
    exceedance_curve: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary representation."""
        return {
            'expected_loss': self.expected_loss,
            'standard_deviation': self.standard_deviation,
            'variance': self.variance,
            'minimum_loss': self.minimum_loss,
            'maximum_loss': self.maximum_loss,
            'var_95': self.var_95,
            'var_99': self.var_99,
            'var_99_9': self.var_99_9,
            'tvar_95': self.tvar_95,
            'tvar_99': self.tvar_99,
            'tvar_99_9': self.tvar_99_9,
            'skewness': self.skewness,
            'kurtosis': self.kurtosis,
            'coefficient_of_variation': self.coefficient_of_variation,
            'probability_of_loss': self.probability_of_loss,
            'median_loss': self.median_loss,
            'mode_loss': self.mode_loss,
            'percentiles': self.percentiles,
            'histogram_data': self.histogram_data,
            'exceedance_curve': self.exceedance_curve
        }


class RiskMetricsCalculator:
    """Calculator for various risk metrics from simulation results."""
    
    def __init__(self, confidence_levels: Optional[List[float]] = None):
        """
        Initialize the risk metrics calculator.
        
        Args:
            confidence_levels: List of confidence levels for VaR/TVaR calculations
        """
        self.confidence_levels = confidence_levels or [0.95, 0.99, 0.999]
        self.default_percentiles = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.999]
    
    def calculate_metrics(
        self,
        losses: np.ndarray,
        percentile_levels: Optional[List[float]] = None,
        include_distribution_data: bool = True
    ) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics from loss data.
        
        Args:
            losses: Array of simulated losses
            percentile_levels: Custom percentile levels to calculate
            include_distribution_data: Whether to include histogram and exceedance data
            
        Returns:
            RiskMetrics object containing all calculated metrics
        """
        try:
            if len(losses) == 0:
                raise SimulationError("Cannot calculate metrics from empty loss array")
            
            # Remove any NaN or infinite values
            losses = self._clean_loss_data(losses)
            
            if len(losses) == 0:
                raise SimulationError("No valid loss data after cleaning")
            
            # Basic statistics
            expected_loss = np.mean(losses)
            std_dev = np.std(losses, ddof=1)
            variance = np.var(losses, ddof=1)
            min_loss = np.min(losses)
            max_loss = np.max(losses)
            median_loss = np.median(losses)
            
            # Risk measures
            var_metrics = self._calculate_var(losses)
            tvar_metrics = self._calculate_tvar(losses)
            
            # Distribution properties
            skewness = stats.skew(losses)
            kurtosis = stats.kurtosis(losses)
            cv = std_dev / expected_loss if expected_loss > 0 else np.inf
            
            # Additional metrics
            prob_of_loss = np.mean(losses > 0)
            mode_loss = self._calculate_mode(losses)
            
            # Percentiles
            percentiles = None
            if percentile_levels:
                percentiles = self._calculate_percentiles(losses, percentile_levels)
            else:
                percentiles = self._calculate_percentiles(losses, self.default_percentiles)
            
            # Distribution data for visualization
            histogram_data = None
            exceedance_curve = None
            if include_distribution_data:
                histogram_data = self._create_histogram_data(losses)
                exceedance_curve = self._create_exceedance_curve(losses)
            
            return RiskMetrics(
                expected_loss=expected_loss,
                standard_deviation=std_dev,
                variance=variance,
                minimum_loss=min_loss,
                maximum_loss=max_loss,
                var_95=var_metrics.get(0.95, 0.0),
                var_99=var_metrics.get(0.99, 0.0),
                var_99_9=var_metrics.get(0.999, 0.0),
                tvar_95=tvar_metrics.get(0.95, 0.0),
                tvar_99=tvar_metrics.get(0.99, 0.0),
                tvar_99_9=tvar_metrics.get(0.999, 0.0),
                skewness=skewness,
                kurtosis=kurtosis,
                coefficient_of_variation=cv,
                probability_of_loss=prob_of_loss,
                median_loss=median_loss,
                mode_loss=mode_loss,
                percentiles=percentiles,
                histogram_data=histogram_data,
                exceedance_curve=exceedance_curve
            )
            
        except Exception as e:
            raise SimulationError(f"Error calculating risk metrics: {str(e)}")
    
    def _clean_loss_data(self, losses: np.ndarray) -> np.ndarray:
        """Remove invalid values from loss data."""
        # Remove NaN and infinite values
        valid_mask = np.isfinite(losses)
        cleaned_losses = losses[valid_mask]
        
        # Remove negative losses (shouldn't happen but safety check)
        cleaned_losses = cleaned_losses[cleaned_losses >= 0]
        
        return cleaned_losses
    
    def _calculate_var(self, losses: np.ndarray) -> Dict[float, float]:
        """Calculate Value at Risk for specified confidence levels."""
        var_results = {}
        
        for confidence_level in self.confidence_levels:
            percentile = confidence_level * 100
            var_value = np.percentile(losses, percentile)
            var_results[confidence_level] = var_value
        
        return var_results
    
    def _calculate_tvar(self, losses: np.ndarray) -> Dict[float, float]:
        """Calculate Tail Value at Risk (Expected Shortfall) for specified confidence levels."""
        tvar_results = {}
        
        for confidence_level in self.confidence_levels:
            var_threshold = np.percentile(losses, confidence_level * 100)
            tail_losses = losses[losses >= var_threshold]
            
            if len(tail_losses) > 0:
                tvar_value = np.mean(tail_losses)
            else:
                tvar_value = var_threshold
            
            tvar_results[confidence_level] = tvar_value
        
        return tvar_results
    
    def _calculate_mode(self, losses: np.ndarray) -> Optional[float]:
        """Calculate the mode of the loss distribution."""
        try:
            # For continuous data, we'll use a histogram-based approach
            hist, bin_edges = np.histogram(losses, bins='auto')
            max_bin_index = np.argmax(hist)
            mode_estimate = (bin_edges[max_bin_index] + bin_edges[max_bin_index + 1]) / 2
            return mode_estimate
        except Exception:
            return None
    
    def _calculate_percentiles(self, losses: np.ndarray, percentile_levels: List[float]) -> Dict[str, float]:
        """Calculate specified percentiles."""
        percentiles = {}
        
        for p in percentile_levels:
            percentile_value = np.percentile(losses, p * 100)
            percentiles[f"{p:.3f}"] = percentile_value
        
        return percentiles
    
    def _create_histogram_data(self, losses: np.ndarray, bins: Union[int, str] = 'auto') -> Dict[str, Any]:
        """Create histogram data for visualization."""
        try:
            hist, bin_edges = np.histogram(losses, bins=bins)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            return {
                'counts': hist.tolist(),
                'bin_edges': bin_edges.tolist(),
                'bin_centers': bin_centers.tolist(),
                'bin_width': bin_edges[1] - bin_edges[0] if len(bin_edges) > 1 else 0,
                'total_observations': len(losses)
            }
        except Exception as e:
            raise SimulationError(f"Error creating histogram data: {str(e)}")
    
    def _create_exceedance_curve(self, losses: np.ndarray, num_points: int = 100) -> Dict[str, Any]:
        """Create exceedance probability curve data."""
        try:
            # Sort losses in descending order
            sorted_losses = np.sort(losses)[::-1]
            
            # Create exceedance points
            if len(sorted_losses) <= num_points:
                loss_levels = sorted_losses
                exceedance_probs = np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)
            else:
                # Sample evenly spaced points
                indices = np.linspace(0, len(sorted_losses) - 1, num_points, dtype=int)
                loss_levels = sorted_losses[indices]
                exceedance_probs = (indices + 1) / len(sorted_losses)
            
            return {
                'loss_levels': loss_levels.tolist(),
                'exceedance_probabilities': exceedance_probs.tolist(),
                'return_periods': (1 / exceedance_probs).tolist()
            }
        except Exception as e:
            raise SimulationError(f"Error creating exceedance curve: {str(e)}")
    
    def calculate_portfolio_metrics(
        self,
        portfolio_losses: Dict[str, np.ndarray],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, RiskMetrics]:
        """
        Calculate risk metrics for a portfolio of different loss sources.
        
        Args:
            portfolio_losses: Dictionary mapping source names to loss arrays
            weights: Optional weights for combining sources
            
        Returns:
            Dictionary mapping source names to their risk metrics
        """
        try:
            results = {}
            
            # Calculate metrics for each source
            for source_name, losses in portfolio_losses.items():
                if len(losses) > 0:
                    weight = weights.get(source_name, 1.0) if weights else 1.0
                    weighted_losses = losses * weight
                    results[source_name] = self.calculate_metrics(weighted_losses)
            
            # Calculate combined portfolio metrics if multiple sources
            if len(portfolio_losses) > 1:
                # Simple aggregation (assumes independence)
                total_losses = np.zeros(len(next(iter(portfolio_losses.values()))))
                
                for source_name, losses in portfolio_losses.items():
                    weight = weights.get(source_name, 1.0) if weights else 1.0
                    total_losses += losses * weight
                
                results['total_portfolio'] = self.calculate_metrics(total_losses)
            
            return results
            
        except Exception as e:
            raise SimulationError(f"Error calculating portfolio metrics: {str(e)}")
    
    def compare_scenarios(
        self,
        baseline_losses: np.ndarray,
        scenario_losses: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare risk metrics between baseline and various scenarios.
        
        Args:
            baseline_losses: Baseline scenario loss data
            scenario_losses: Dictionary mapping scenario names to loss arrays
            
        Returns:
            Dictionary with comparison results for each scenario
        """
        try:
            baseline_metrics = self.calculate_metrics(baseline_losses, include_distribution_data=False)
            comparison_results = {}
            
            for scenario_name, losses in scenario_losses.items():
                scenario_metrics = self.calculate_metrics(losses, include_distribution_data=False)
                
                # Calculate percentage changes
                comparison = {
                    'expected_loss_change': self._calculate_percentage_change(
                        baseline_metrics.expected_loss, scenario_metrics.expected_loss
                    ),
                    'var_95_change': self._calculate_percentage_change(
                        baseline_metrics.var_95, scenario_metrics.var_95
                    ),
                    'var_99_change': self._calculate_percentage_change(
                        baseline_metrics.var_99, scenario_metrics.var_99
                    ),
                    'tvar_95_change': self._calculate_percentage_change(
                        baseline_metrics.tvar_95, scenario_metrics.tvar_95
                    ),
                    'tvar_99_change': self._calculate_percentage_change(
                        baseline_metrics.tvar_99, scenario_metrics.tvar_99
                    ),
                    'std_dev_change': self._calculate_percentage_change(
                        baseline_metrics.standard_deviation, scenario_metrics.standard_deviation
                    ),
                    'max_loss_change': self._calculate_percentage_change(
                        baseline_metrics.maximum_loss, scenario_metrics.maximum_loss
                    )
                }
                
                comparison_results[scenario_name] = comparison
            
            return comparison_results
            
        except Exception as e:
            raise SimulationError(f"Error comparing scenarios: {str(e)}")
    
    def _calculate_percentage_change(self, baseline: float, scenario: float) -> float:
        """Calculate percentage change between baseline and scenario."""
        if baseline == 0:
            return float('inf') if scenario > 0 else 0.0
        return ((scenario - baseline) / baseline) * 100
    
    def calculate_confidence_intervals(
        self,
        losses: np.ndarray,
        confidence_level: float = 0.95,
        method: str = 'bootstrap',
        n_bootstrap: int = 1000
    ) -> Dict[str, Tuple[float, float]]:
        """
        Calculate confidence intervals for key risk metrics.
        
        Args:
            losses: Loss data array
            confidence_level: Confidence level for intervals
            method: Method for calculating intervals ('bootstrap' or 'analytical')
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            Dictionary with confidence intervals for key metrics
        """
        try:
            if method == 'bootstrap':
                return self._bootstrap_confidence_intervals(losses, confidence_level, n_bootstrap)
            else:
                return self._analytical_confidence_intervals(losses, confidence_level)
                
        except Exception as e:
            raise SimulationError(f"Error calculating confidence intervals: {str(e)}")
    
    def _bootstrap_confidence_intervals(
        self,
        losses: np.ndarray,
        confidence_level: float,
        n_bootstrap: int
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate bootstrap confidence intervals."""
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        # Bootstrap samples
        bootstrap_means = []
        bootstrap_var95 = []
        bootstrap_var99 = []
        
        for _ in range(n_bootstrap):
            sample = np.random.choice(losses, size=len(losses), replace=True)
            bootstrap_means.append(np.mean(sample))
            bootstrap_var95.append(np.percentile(sample, 95))
            bootstrap_var99.append(np.percentile(sample, 99))
        
        results = {
            'expected_loss': (
                np.percentile(bootstrap_means, lower_percentile),
                np.percentile(bootstrap_means, upper_percentile)
            ),
            'var_95': (
                np.percentile(bootstrap_var95, lower_percentile),
                np.percentile(bootstrap_var95, upper_percentile)
            ),
            'var_99': (
                np.percentile(bootstrap_var99, lower_percentile),
                np.percentile(bootstrap_var99, upper_percentile)
            )
        }
        
        return results
    
    def _analytical_confidence_intervals(
        self,
        losses: np.ndarray,
        confidence_level: float
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate analytical confidence intervals using normal approximation."""
        n = len(losses)
        mean = np.mean(losses)
        std = np.std(losses, ddof=1)
        se_mean = std / np.sqrt(n)
        
        # Critical value for normal distribution
        alpha = 1 - confidence_level
        z_critical = stats.norm.ppf(1 - alpha / 2)
        
        # Confidence interval for mean
        mean_ci = (
            mean - z_critical * se_mean,
            mean + z_critical * se_mean
        )
        
        return {
            'expected_loss': mean_ci
        } 