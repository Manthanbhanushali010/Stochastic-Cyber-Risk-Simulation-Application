"""
Main simulation engine for cyber risk Monte Carlo simulation.

This module contains the core simulation engine that orchestrates
frequency and severity modeling, financial calculations, and risk metrics.
"""

import numpy as np
import logging
import time
from typing import Dict, Any, List, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict

from .parameters import SimulationParameters, EventParameters
from .distributions import DistributionFactory
from .financial import FinancialCalculator, PolicyTerms
from .metrics import RiskMetricsCalculator, RiskMetrics
from .exceptions import SimulationError, ParameterError, ConvergenceError

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Core Monte Carlo simulation engine for cyber risk events."""
    
    def __init__(self, progress_callback: Optional[Callable[[int, int], None]] = None):
        """
        Initialize the simulation engine.
        
        Args:
            progress_callback: Optional callback function for progress updates
        """
        self.progress_callback = progress_callback
        self.financial_calculator = FinancialCalculator()
        self.metrics_calculator = RiskMetricsCalculator()
        self.random_state = None
        
        # Simulation state
        self.is_running = False
        self.should_stop = False
        self.current_iteration = 0
        
    def run_simulation(
        self,
        parameters: SimulationParameters,
        portfolio_policies: Optional[Dict[str, PolicyTerms]] = None
    ) -> Dict[str, Any]:
        """
        Run a complete Monte Carlo simulation.
        
        Args:
            parameters: Simulation configuration parameters
            portfolio_policies: Dictionary of policy terms for portfolio simulation
            
        Returns:
            Dictionary containing simulation results and metrics
        """
        try:
            logger.info(f"Starting simulation with {parameters.num_iterations} iterations")
            start_time = time.time()
            
            # Validate parameters
            parameters.validate()
            
            # Initialize simulation state
            self._initialize_simulation(parameters)
            
            # Run the simulation
            simulation_results = self._execute_simulation(parameters, portfolio_policies)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(simulation_results, parameters)
            
            # Prepare final results
            end_time = time.time()
            duration = end_time - start_time
            
            results = {
                'simulation_parameters': parameters.to_dict(),
                'execution_time': duration,
                'total_iterations': parameters.num_iterations,
                'loss_data': simulation_results,
                'risk_metrics': risk_metrics.to_dict(),
                'convergence_info': self._check_convergence(simulation_results, parameters),
                'summary_statistics': self._create_summary_statistics(risk_metrics)
            }
            
            logger.info(f"Simulation completed in {duration:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            raise SimulationError(f"Simulation execution failed: {str(e)}")
        finally:
            self.is_running = False
            self.should_stop = False
    
    def _initialize_simulation(self, parameters: SimulationParameters) -> None:
        """Initialize simulation state and random number generator."""
        self.is_running = True
        self.should_stop = False
        self.current_iteration = 0
        
        # Set up random state
        if parameters.random_seed is not None:
            self.random_state = np.random.RandomState(parameters.random_seed)
        else:
            self.random_state = np.random.RandomState()
    
    def _execute_simulation(
        self,
        parameters: SimulationParameters,
        portfolio_policies: Optional[Dict[str, PolicyTerms]]
    ) -> Dict[str, Any]:
        """Execute the main simulation loop."""
        
        # Create distributions
        frequency_dist = DistributionFactory.create_frequency_distribution(
            parameters.event_params.frequency_distribution,
            parameters.event_params.frequency_params
        )
        
        severity_dist = DistributionFactory.create_severity_distribution(
            parameters.event_params.severity_distribution,
            parameters.event_params.severity_params
        )
        
        # Initialize result arrays
        aggregate_losses = np.zeros(parameters.num_iterations)
        iteration_details = []
        
        if parameters.parallel_processing and parameters.max_workers != 1:
            # Parallel execution
            results = self._run_parallel_simulation(
                parameters, frequency_dist, severity_dist, portfolio_policies
            )
            aggregate_losses = results['aggregate_losses']
            iteration_details = results['iteration_details']
        else:
            # Sequential execution
            for i in range(parameters.num_iterations):
                if self.should_stop:
                    break
                
                # Generate number of events for this iteration
                num_events = frequency_dist.sample(1, self.random_state)[0]
                
                # Generate event severities
                if num_events > 0:
                    # Limit number of events per iteration for performance
                    num_events = min(num_events, parameters.max_events_per_iteration)
                    event_severities = severity_dist.sample(num_events, self.random_state)
                    
                    # Calculate financial impact
                    if portfolio_policies:
                        iteration_loss = self._calculate_portfolio_iteration_loss(
                            event_severities, portfolio_policies, parameters
                        )
                    else:
                        # Simple aggregation for single policy or ground-up losses
                        iteration_loss = np.sum(event_severities)
                else:
                    iteration_loss = 0.0
                
                aggregate_losses[i] = iteration_loss
                
                if parameters.save_raw_losses:
                    iteration_details.append({
                        'iteration': i,
                        'num_events': num_events,
                        'total_loss': iteration_loss
                    })
                
                self.current_iteration = i + 1
                
                # Progress callback
                if self.progress_callback and (i + 1) % 1000 == 0:
                    self.progress_callback(i + 1, parameters.num_iterations)
        
        return {
            'aggregate_losses': aggregate_losses[:self.current_iteration],
            'iteration_details': iteration_details if parameters.save_raw_losses else None,
            'completed_iterations': self.current_iteration
        }
    
    def _run_parallel_simulation(
        self,
        parameters: SimulationParameters,
        frequency_dist,
        severity_dist,
        portfolio_policies: Optional[Dict[str, PolicyTerms]]
    ) -> Dict[str, Any]:
        """Run simulation using parallel processing."""
        
        num_workers = parameters.max_workers or min(4, parameters.num_iterations // 1000)
        batch_size = parameters.batch_size
        
        # Split iterations into batches
        batches = []
        for start_idx in range(0, parameters.num_iterations, batch_size):
            end_idx = min(start_idx + batch_size, parameters.num_iterations)
            batches.append((start_idx, end_idx))
        
        aggregate_losses = np.zeros(parameters.num_iterations)
        iteration_details = []
        completed_iterations = 0
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit batch jobs
            future_to_batch = {
                executor.submit(
                    self._run_simulation_batch,
                    batch_start, batch_end, parameters, frequency_dist, severity_dist, portfolio_policies
                ): (batch_start, batch_end)
                for batch_start, batch_end in batches
            }
            
            # Collect results
            for future in as_completed(future_to_batch):
                if self.should_stop:
                    break
                
                batch_start, batch_end = future_to_batch[future]
                try:
                    batch_results = future.result()
                    
                    # Store results
                    batch_size_actual = batch_end - batch_start
                    aggregate_losses[batch_start:batch_end] = batch_results['losses']
                    
                    if parameters.save_raw_losses and batch_results['details']:
                        iteration_details.extend(batch_results['details'])
                    
                    completed_iterations += batch_size_actual
                    
                    # Progress callback
                    if self.progress_callback:
                        self.progress_callback(completed_iterations, parameters.num_iterations)
                        
                except Exception as e:
                    logger.error(f"Batch simulation failed: {str(e)}")
                    raise SimulationError(f"Parallel simulation batch failed: {str(e)}")
        
        self.current_iteration = completed_iterations
        
        return {
            'aggregate_losses': aggregate_losses[:completed_iterations],
            'iteration_details': iteration_details if parameters.save_raw_losses else None,
            'completed_iterations': completed_iterations
        }
    
    def _run_simulation_batch(
        self,
        start_idx: int,
        end_idx: int,
        parameters: SimulationParameters,
        frequency_dist,
        severity_dist,
        portfolio_policies: Optional[Dict[str, PolicyTerms]]
    ) -> Dict[str, Any]:
        """Run a batch of simulation iterations."""
        
        batch_size = end_idx - start_idx
        batch_losses = np.zeros(batch_size)
        batch_details = []
        
        # Create separate random state for this batch
        batch_random_state = np.random.RandomState(
            parameters.random_seed + start_idx if parameters.random_seed else None
        )
        
        for i in range(batch_size):
            # Generate number of events
            num_events = frequency_dist.sample(1, batch_random_state)[0]
            
            # Generate event severities
            if num_events > 0:
                num_events = min(num_events, parameters.max_events_per_iteration)
                event_severities = severity_dist.sample(num_events, batch_random_state)
                
                # Calculate financial impact
                if portfolio_policies:
                    iteration_loss = self._calculate_portfolio_iteration_loss(
                        event_severities, portfolio_policies, parameters
                    )
                else:
                    iteration_loss = np.sum(event_severities)
            else:
                iteration_loss = 0.0
            
            batch_losses[i] = iteration_loss
            
            if parameters.save_raw_losses:
                batch_details.append({
                    'iteration': start_idx + i,
                    'num_events': num_events,
                    'total_loss': iteration_loss
                })
        
        return {
            'losses': batch_losses,
            'details': batch_details if parameters.save_raw_losses else None
        }
    
    def _calculate_portfolio_iteration_loss(
        self,
        event_severities: np.ndarray,
        portfolio_policies: Dict[str, PolicyTerms],
        parameters: SimulationParameters
    ) -> float:
        """Calculate total loss for a portfolio in a single iteration."""
        
        # For simplicity, assume each event affects all policies
        # In practice, this would be more sophisticated with correlation modeling
        
        total_loss = 0.0
        
        for policy_id, policy_terms in portfolio_policies.items():
            # Calculate policy-specific loss
            if len(event_severities) > 0:
                # Use vectorized calculation for performance
                policy_losses = self.financial_calculator.calculate_batch_losses(
                    event_severities, policy_terms
                )
                policy_total = np.sum(policy_losses)
            else:
                policy_total = 0.0
            
            total_loss += policy_total
        
        return total_loss
    
    def _calculate_risk_metrics(
        self,
        simulation_results: Dict[str, Any],
        parameters: SimulationParameters
    ) -> RiskMetrics:
        """Calculate comprehensive risk metrics from simulation results."""
        
        aggregate_losses = simulation_results['aggregate_losses']
        
        if len(aggregate_losses) == 0:
            raise SimulationError("No simulation results to analyze")
        
        return self.metrics_calculator.calculate_metrics(
            aggregate_losses,
            percentile_levels=parameters.percentile_levels if parameters.calculate_percentiles else None,
            include_distribution_data=True
        )
    
    def _check_convergence(
        self,
        simulation_results: Dict[str, Any],
        parameters: SimulationParameters
    ) -> Dict[str, Any]:
        """Check simulation convergence if enabled."""
        
        convergence_info = {
            'convergence_enabled': parameters.convergence_check,
            'converged': False,
            'convergence_iteration': None,
            'final_variance': None
        }
        
        if not parameters.convergence_check:
            return convergence_info
        
        losses = simulation_results['aggregate_losses']
        window_size = parameters.convergence_window
        threshold = parameters.convergence_threshold
        
        if len(losses) < window_size * 2:
            return convergence_info
        
        # Check convergence using rolling mean variance
        for i in range(window_size, len(losses) - window_size):
            window1_mean = np.mean(losses[i-window_size:i])
            window2_mean = np.mean(losses[i:i+window_size])
            
            relative_change = abs(window2_mean - window1_mean) / abs(window1_mean) if window1_mean != 0 else 0
            
            if relative_change < threshold:
                convergence_info.update({
                    'converged': True,
                    'convergence_iteration': i,
                    'final_variance': relative_change
                })
                break
        
        return convergence_info
    
    def _create_summary_statistics(self, risk_metrics: RiskMetrics) -> Dict[str, Any]:
        """Create summary statistics for quick reference."""
        
        return {
            'expected_annual_loss': risk_metrics.expected_loss,
            'probability_of_any_loss': risk_metrics.probability_of_loss,
            'value_at_risk': {
                '95th_percentile': risk_metrics.var_95,
                '99th_percentile': risk_metrics.var_99,
                '99.9th_percentile': risk_metrics.var_99_9
            },
            'tail_value_at_risk': {
                '95th_percentile': risk_metrics.tvar_95,
                '99th_percentile': risk_metrics.tvar_99,
                '99.9th_percentile': risk_metrics.tvar_99_9
            },
            'distribution_shape': {
                'standard_deviation': risk_metrics.standard_deviation,
                'coefficient_of_variation': risk_metrics.coefficient_of_variation,
                'skewness': risk_metrics.skewness,
                'kurtosis': risk_metrics.kurtosis
            },
            'loss_range': {
                'minimum': risk_metrics.minimum_loss,
                'median': risk_metrics.median_loss,
                'maximum': risk_metrics.maximum_loss
            }
        }
    
    def stop_simulation(self) -> None:
        """Stop the running simulation."""
        self.should_stop = True
        logger.info("Simulation stop requested")
    
    def get_simulation_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        return {
            'is_running': self.is_running,
            'current_iteration': self.current_iteration,
            'should_stop': self.should_stop
        }
    
    def run_scenario_comparison(
        self,
        base_parameters: SimulationParameters,
        scenario_parameters: Dict[str, SimulationParameters],
        portfolio_policies: Optional[Dict[str, PolicyTerms]] = None
    ) -> Dict[str, Any]:
        """
        Run multiple scenarios and compare results.
        
        Args:
            base_parameters: Baseline simulation parameters
            scenario_parameters: Dictionary mapping scenario names to parameters
            portfolio_policies: Portfolio policy terms
            
        Returns:
            Dictionary containing comparison results
        """
        try:
            logger.info("Starting scenario comparison analysis")
            
            # Run baseline simulation
            baseline_results = self.run_simulation(base_parameters, portfolio_policies)
            baseline_losses = baseline_results['loss_data']['aggregate_losses']
            
            # Run scenario simulations
            scenario_results = {}
            scenario_losses = {}
            
            for scenario_name, params in scenario_parameters.items():
                logger.info(f"Running scenario: {scenario_name}")
                scenario_result = self.run_simulation(params, portfolio_policies)
                scenario_results[scenario_name] = scenario_result
                scenario_losses[scenario_name] = scenario_result['loss_data']['aggregate_losses']
            
            # Compare scenarios
            comparison = self.metrics_calculator.compare_scenarios(baseline_losses, scenario_losses)
            
            return {
                'baseline_results': baseline_results,
                'scenario_results': scenario_results,
                'scenario_comparison': comparison,
                'summary': self._create_scenario_summary(comparison)
            }
            
        except Exception as e:
            logger.error(f"Scenario comparison failed: {str(e)}")
            raise SimulationError(f"Scenario comparison failed: {str(e)}")
    
    def _create_scenario_summary(self, comparison: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Create summary of scenario comparison results."""
        
        summary = {
            'most_severe_scenario': None,
            'least_severe_scenario': None,
            'largest_var_increase': None,
            'largest_expected_loss_increase': None
        }
        
        if not comparison:
            return summary
        
        # Find most/least severe scenarios based on expected loss change
        el_changes = {name: results['expected_loss_change'] for name, results in comparison.items()}
        
        if el_changes:
            summary['most_severe_scenario'] = max(el_changes, key=el_changes.get)
            summary['least_severe_scenario'] = min(el_changes, key=el_changes.get)
        
        # Find largest VaR and expected loss increases
        var_changes = {name: results['var_99_change'] for name, results in comparison.items()}
        if var_changes:
            summary['largest_var_increase'] = max(var_changes, key=var_changes.get)
        
        if el_changes:
            summary['largest_expected_loss_increase'] = max(el_changes, key=el_changes.get)
        
        return summary 