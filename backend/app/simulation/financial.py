"""
Financial impact calculation module for cyber risk simulation.

This module handles the application of insurance policy terms including
deductibles, limits, sub-limits, and reinsurance arrangements.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from .exceptions import FinancialCalculationError


@dataclass
class PolicyTerms:
    """Insurance policy terms and conditions."""
    
    policy_id: str
    coverage_limit: float
    deductible: float = 0.0
    sub_limits: Optional[Dict[str, float]] = None
    coinsurance: float = 0.0  # Percentage of loss shared by insured
    waiting_period: int = 0  # Days before coverage begins
    policy_aggregate: Optional[float] = None  # Annual aggregate limit
    
    def __post_init__(self):
        """Validate policy terms after initialization."""
        if self.coverage_limit <= 0:
            raise FinancialCalculationError(f"Coverage limit must be positive: {self.coverage_limit}")
        if self.deductible < 0:
            raise FinancialCalculationError(f"Deductible cannot be negative: {self.deductible}")
        if not 0 <= self.coinsurance <= 1:
            raise FinancialCalculationError(f"Coinsurance must be between 0 and 1: {self.coinsurance}")
        if self.policy_aggregate is not None and self.policy_aggregate <= 0:
            raise FinancialCalculationError(f"Policy aggregate must be positive: {self.policy_aggregate}")


@dataclass
class ReinsuranceLayer:
    """Reinsurance layer definition."""
    
    layer_type: str  # 'quota_share', 'surplus', 'excess_of_loss', 'stop_loss'
    attachment_point: float = 0.0
    limit: Optional[float] = None
    cession_rate: float = 0.0  # For quota share and surplus
    priority: int = 1  # Layer priority (1 = primary)
    
    def __post_init__(self):
        """Validate reinsurance layer parameters."""
        valid_types = ['quota_share', 'surplus', 'excess_of_loss', 'stop_loss']
        if self.layer_type not in valid_types:
            raise FinancialCalculationError(f"Invalid reinsurance type: {self.layer_type}")
        
        if self.attachment_point < 0:
            raise FinancialCalculationError("Attachment point cannot be negative")
        
        if self.limit is not None and self.limit <= 0:
            raise FinancialCalculationError("Reinsurance limit must be positive")
        
        if not 0 <= self.cession_rate <= 1:
            raise FinancialCalculationError("Cession rate must be between 0 and 1")


class FinancialCalculator:
    """Calculator for insurance financial impacts."""
    
    def __init__(self):
        """Initialize the financial calculator."""
        self.calculation_cache = {}
    
    def calculate_net_loss(
        self,
        ground_up_loss: float,
        policy_terms: PolicyTerms,
        reinsurance_layers: Optional[List[ReinsuranceLayer]] = None,
        event_date: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate net loss after applying policy terms and reinsurance.
        
        Args:
            ground_up_loss: Original loss amount before any adjustments
            policy_terms: Insurance policy terms and conditions
            reinsurance_layers: List of reinsurance arrangements
            event_date: Event date for waiting period calculations
            
        Returns:
            Dictionary containing various loss calculations
        """
        try:
            # Apply waiting period
            if self._is_within_waiting_period(event_date, policy_terms.waiting_period):
                return self._create_loss_breakdown(ground_up_loss, 0.0, 0.0, 0.0, 0.0)
            
            # Apply deductible
            loss_after_deductible = max(0.0, ground_up_loss - policy_terms.deductible)
            
            # Apply coinsurance
            loss_after_coinsurance = loss_after_deductible * (1 - policy_terms.coinsurance)
            
            # Apply policy limit
            covered_loss = min(loss_after_coinsurance, policy_terms.coverage_limit)
            
            # Apply sub-limits if applicable
            covered_loss = self._apply_sub_limits(covered_loss, policy_terms.sub_limits)
            
            # Calculate insurer's gross loss (before reinsurance)
            insurer_gross_loss = covered_loss
            
            # Apply reinsurance
            reinsurance_recovery = 0.0
            if reinsurance_layers:
                reinsurance_recovery = self._calculate_reinsurance_recovery(
                    insurer_gross_loss, reinsurance_layers
                )
            
            # Calculate net loss (insurer's final exposure)
            insurer_net_loss = insurer_gross_loss - reinsurance_recovery
            
            return self._create_loss_breakdown(
                ground_up_loss=ground_up_loss,
                covered_loss=covered_loss,
                insurer_gross_loss=insurer_gross_loss,
                reinsurance_recovery=reinsurance_recovery,
                insurer_net_loss=insurer_net_loss
            )
            
        except Exception as e:
            raise FinancialCalculationError(f"Error calculating net loss: {str(e)}")
    
    def calculate_portfolio_loss(
        self,
        event_losses: Dict[str, float],
        portfolio_policies: Dict[str, PolicyTerms],
        reinsurance_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate total portfolio loss for an event affecting multiple policies.
        
        Args:
            event_losses: Dictionary mapping policy_id to ground-up loss
            portfolio_policies: Dictionary mapping policy_id to PolicyTerms
            reinsurance_config: Portfolio-level reinsurance configuration
            
        Returns:
            Dictionary containing portfolio loss calculations
        """
        try:
            total_ground_up = 0.0
            total_covered = 0.0
            total_gross = 0.0
            total_net = 0.0
            policy_details = {}
            
            # Calculate loss for each policy
            for policy_id, ground_up_loss in event_losses.items():
                if policy_id not in portfolio_policies:
                    continue
                
                policy_terms = portfolio_policies[policy_id]
                
                # Get policy-specific reinsurance if available
                policy_reinsurance = None
                if reinsurance_config and 'policy_specific' in reinsurance_config:
                    policy_reinsurance = reinsurance_config['policy_specific'].get(policy_id)
                
                # Calculate net loss for this policy
                loss_breakdown = self.calculate_net_loss(
                    ground_up_loss, policy_terms, policy_reinsurance
                )
                
                policy_details[policy_id] = loss_breakdown
                
                # Aggregate totals
                total_ground_up += loss_breakdown['ground_up_loss']
                total_covered += loss_breakdown['covered_loss']
                total_gross += loss_breakdown['insurer_gross_loss']
                total_net += loss_breakdown['insurer_net_loss']
            
            # Apply portfolio-level reinsurance
            portfolio_reinsurance_recovery = 0.0
            if reinsurance_config and 'portfolio_level' in reinsurance_config:
                portfolio_layers = [
                    ReinsuranceLayer(**layer) 
                    for layer in reinsurance_config['portfolio_level']
                ]
                portfolio_reinsurance_recovery = self._calculate_reinsurance_recovery(
                    total_gross, portfolio_layers
                )
            
            # Final net loss after portfolio reinsurance
            final_net_loss = total_net - portfolio_reinsurance_recovery
            
            return {
                'total_ground_up_loss': total_ground_up,
                'total_covered_loss': total_covered,
                'total_gross_loss': total_gross,
                'portfolio_reinsurance_recovery': portfolio_reinsurance_recovery,
                'total_net_loss': final_net_loss,
                'policy_details': policy_details,
                'affected_policies': len(event_losses),
                'policies_with_loss': len([loss for loss in event_losses.values() if loss > 0])
            }
            
        except Exception as e:
            raise FinancialCalculationError(f"Error calculating portfolio loss: {str(e)}")
    
    def _is_within_waiting_period(self, event_date: Optional[int], waiting_period: int) -> bool:
        """Check if event occurs within policy waiting period."""
        if event_date is None or waiting_period == 0:
            return False
        return event_date < waiting_period
    
    def _apply_sub_limits(self, covered_loss: float, sub_limits: Optional[Dict[str, float]]) -> float:
        """Apply sub-limits to covered loss."""
        if not sub_limits:
            return covered_loss
        
        # For simplicity, apply the most restrictive sub-limit
        # In practice, this would be more sophisticated based on loss type
        if sub_limits:
            min_sub_limit = min(sub_limits.values())
            return min(covered_loss, min_sub_limit)
        
        return covered_loss
    
    def _calculate_reinsurance_recovery(
        self,
        gross_loss: float,
        reinsurance_layers: List[ReinsuranceLayer]
    ) -> float:
        """Calculate total reinsurance recovery from all layers."""
        if not reinsurance_layers or gross_loss <= 0:
            return 0.0
        
        # Sort layers by priority
        sorted_layers = sorted(reinsurance_layers, key=lambda x: x.priority)
        
        total_recovery = 0.0
        remaining_loss = gross_loss
        
        for layer in sorted_layers:
            if remaining_loss <= 0:
                break
            
            layer_recovery = self._calculate_layer_recovery(remaining_loss, layer)
            total_recovery += layer_recovery
            
            # For excess layers, reduce the remaining loss
            if layer.layer_type in ['excess_of_loss', 'stop_loss']:
                remaining_loss = max(0, remaining_loss - layer_recovery)
        
        return min(total_recovery, gross_loss)
    
    def _calculate_layer_recovery(self, loss: float, layer: ReinsuranceLayer) -> float:
        """Calculate recovery from a single reinsurance layer."""
        if loss <= 0:
            return 0.0
        
        if layer.layer_type == 'quota_share':
            return loss * layer.cession_rate
        
        elif layer.layer_type == 'surplus':
            # Simplified surplus calculation
            return min(loss, layer.limit or float('inf')) * layer.cession_rate
        
        elif layer.layer_type == 'excess_of_loss':
            if loss <= layer.attachment_point:
                return 0.0
            excess_loss = loss - layer.attachment_point
            return min(excess_loss, layer.limit or float('inf'))
        
        elif layer.layer_type == 'stop_loss':
            if loss <= layer.attachment_point:
                return 0.0
            stop_loss_recovery = (loss - layer.attachment_point) * layer.cession_rate
            return min(stop_loss_recovery, layer.limit or float('inf'))
        
        return 0.0
    
    def _create_loss_breakdown(
        self,
        ground_up_loss: float,
        covered_loss: float,
        insurer_gross_loss: float,
        reinsurance_recovery: float,
        insurer_net_loss: float
    ) -> Dict[str, float]:
        """Create standardized loss breakdown dictionary."""
        return {
            'ground_up_loss': ground_up_loss,
            'covered_loss': covered_loss,
            'insurer_gross_loss': insurer_gross_loss,
            'reinsurance_recovery': reinsurance_recovery,
            'insurer_net_loss': insurer_net_loss,
            'retention_ratio': insurer_net_loss / ground_up_loss if ground_up_loss > 0 else 0.0,
            'coverage_ratio': covered_loss / ground_up_loss if ground_up_loss > 0 else 0.0
        }
    
    def calculate_batch_losses(
        self,
        losses: np.ndarray,
        policy_terms: PolicyTerms,
        reinsurance_layers: Optional[List[ReinsuranceLayer]] = None
    ) -> np.ndarray:
        """
        Vectorized calculation of net losses for a batch of ground-up losses.
        Optimized for simulation performance.
        
        Args:
            losses: Array of ground-up losses
            policy_terms: Policy terms to apply
            reinsurance_layers: Reinsurance arrangements
            
        Returns:
            Array of net losses
        """
        try:
            # Vectorized deductible application
            losses_after_deductible = np.maximum(0.0, losses - policy_terms.deductible)
            
            # Vectorized coinsurance application
            losses_after_coinsurance = losses_after_deductible * (1 - policy_terms.coinsurance)
            
            # Vectorized limit application
            covered_losses = np.minimum(losses_after_coinsurance, policy_terms.coverage_limit)
            
            # Apply sub-limits (simplified for vectorization)
            if policy_terms.sub_limits:
                min_sub_limit = min(policy_terms.sub_limits.values())
                covered_losses = np.minimum(covered_losses, min_sub_limit)
            
            # For simplicity in vectorized calculations, apply only quota share reinsurance
            if reinsurance_layers:
                quota_share_layers = [layer for layer in reinsurance_layers 
                                    if layer.layer_type == 'quota_share']
                if quota_share_layers:
                    total_cession = sum(layer.cession_rate for layer in quota_share_layers)
                    covered_losses = covered_losses * (1 - min(total_cession, 1.0))
            
            return covered_losses
            
        except Exception as e:
            raise FinancialCalculationError(f"Error in batch loss calculation: {str(e)}")
    
    def estimate_maximum_loss(
        self,
        portfolio_policies: Dict[str, PolicyTerms],
        correlation_factor: float = 1.0
    ) -> Dict[str, float]:
        """
        Estimate maximum possible loss for the portfolio.
        
        Args:
            portfolio_policies: Dictionary of policy terms
            correlation_factor: Factor representing correlation between policies (0-1)
            
        Returns:
            Dictionary with maximum loss estimates
        """
        try:
            total_limits = sum(policy.coverage_limit for policy in portfolio_policies.values())
            total_deductibles = sum(policy.deductible for policy in portfolio_policies.values())
            
            # Theoretical maximum (all policies hit their limits)
            theoretical_max = total_limits
            
            # Correlated maximum (considering correlation between policies)
            correlated_max = theoretical_max * correlation_factor
            
            # Practical maximum (considering typical loss patterns)
            practical_max = correlated_max * 0.8  # Rule of thumb: 80% of theoretical
            
            return {
                'theoretical_maximum': theoretical_max,
                'correlated_maximum': correlated_max,
                'practical_maximum': practical_max,
                'total_deductibles': total_deductibles,
                'net_maximum': practical_max - total_deductibles,
                'policy_count': len(portfolio_policies)
            }
            
        except Exception as e:
            raise FinancialCalculationError(f"Error estimating maximum loss: {str(e)}") 