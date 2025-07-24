from datetime import datetime, timezone
import uuid
import json
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(120), unique=True, nullable=False, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    role = Column(String(20), nullable=False, default='user')  # 'user', 'admin', 'analyst'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    simulation_runs = relationship('SimulationRun', backref='user', lazy='dynamic')
    portfolios = relationship('Portfolio', backref='user', lazy='dynamic')
    scenarios = relationship('Scenario', backref='user', lazy='dynamic')
    
    def set_password(self, password: str):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    @hybrid_property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation."""
        return {
            'id': str(self.id),
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Portfolio(db.Model):
    """Insurance portfolio model containing policies and their details."""
    
    __tablename__ = 'portfolios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Portfolio configuration
    configuration = Column(JSON, nullable=False, default=dict)
    
    # Relationships
    policies = relationship('Policy', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    simulation_runs = relationship('SimulationRun', backref='portfolio', lazy='dynamic')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'configuration': self.configuration,
            'policy_count': self.policies.count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Policy(db.Model):
    """Individual insurance policy within a portfolio."""
    
    __tablename__ = 'policies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey('portfolios.id'), nullable=False)
    policy_number = Column(String(50), nullable=False)
    policyholder_name = Column(String(100), nullable=False)
    
    # Coverage details
    coverage_type = Column(String(50), nullable=False)  # 'cyber_liability', 'data_breach', etc.
    coverage_limit = Column(Float, nullable=False)
    deductible = Column(Float, nullable=False, default=0.0)
    
    # Sub-limits for specific coverage types
    sub_limits = Column(JSON, nullable=True, default=dict)
    
    # Premium and financial details
    annual_premium = Column(Float, nullable=True)
    
    # Policy terms
    policy_start_date = Column(DateTime, nullable=False)
    policy_end_date = Column(DateTime, nullable=False)
    
    # Industry and risk characteristics
    industry_sector = Column(String(50), nullable=True)
    company_size = Column(String(20), nullable=True)  # 'small', 'medium', 'large', 'enterprise'
    risk_score = Column(Float, nullable=True)  # Internal risk assessment score
    
    # Geographic information
    country = Column(String(2), nullable=True)  # ISO country code
    region = Column(String(50), nullable=True)
    
    # Additional policy attributes
    attributes = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary representation."""
        return {
            'id': str(self.id),
            'policy_number': self.policy_number,
            'policyholder_name': self.policyholder_name,
            'coverage_type': self.coverage_type,
            'coverage_limit': self.coverage_limit,
            'deductible': self.deductible,
            'sub_limits': self.sub_limits,
            'annual_premium': self.annual_premium,
            'policy_start_date': self.policy_start_date.isoformat(),
            'policy_end_date': self.policy_end_date.isoformat(),
            'industry_sector': self.industry_sector,
            'company_size': self.company_size,
            'risk_score': self.risk_score,
            'country': self.country,
            'region': self.region,
            'attributes': self.attributes
        }


class SimulationRun(db.Model):
    """Model representing a complete simulation run with parameters and results."""
    
    __tablename__ = 'simulation_runs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey('portfolios.id'), nullable=True)
    scenario_id = Column(UUID(as_uuid=True), ForeignKey('scenarios.id'), nullable=True)
    
    # Run metadata
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='pending')  # 'pending', 'running', 'completed', 'failed'
    
    # Simulation parameters
    num_iterations = Column(Integer, nullable=False)
    random_seed = Column(Integer, nullable=True)
    
    # Event parameters (stored as JSON for flexibility)
    event_parameters = Column(JSON, nullable=False)
    
    # Simulation configuration
    simulation_config = Column(JSON, nullable=True, default=dict)
    
    # Timing information
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Progress tracking
    progress_percent = Column(Float, default=0.0, nullable=False)
    current_iteration = Column(Integer, default=0, nullable=False)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    
    # Relationships
    results = relationship('SimulationResult', backref='simulation_run', 
                          uselist=False, cascade='all, delete-orphan')
    
    @hybrid_property
    def duration(self) -> Optional[float]:
        """Calculate simulation duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert simulation run to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'num_iterations': self.num_iterations,
            'random_seed': self.random_seed,
            'event_parameters': self.event_parameters,
            'simulation_config': self.simulation_config,
            'progress_percent': self.progress_percent,
            'current_iteration': self.current_iteration,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration': self.duration,
            'error_message': self.error_message
        }


class SimulationResult(db.Model):
    """Model storing aggregated results from a simulation run."""
    
    __tablename__ = 'simulation_results'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id = Column(UUID(as_uuid=True), ForeignKey('simulation_runs.id'), nullable=False)
    
    # Aggregated metrics
    expected_loss = Column(Float, nullable=False)
    var_95 = Column(Float, nullable=False)
    var_99 = Column(Float, nullable=False)
    var_99_9 = Column(Float, nullable=False)
    tvar_95 = Column(Float, nullable=False)
    tvar_99 = Column(Float, nullable=False)
    tvar_99_9 = Column(Float, nullable=False)
    
    # Distribution statistics
    min_loss = Column(Float, nullable=False)
    max_loss = Column(Float, nullable=False)
    std_deviation = Column(Float, nullable=False)
    skewness = Column(Float, nullable=True)
    kurtosis = Column(Float, nullable=True)
    
    # Distribution data (stored as compressed JSON)
    loss_distribution = Column(JSON, nullable=True)  # Histogram bins and counts
    percentiles = Column(JSON, nullable=True)  # Key percentiles (1%, 5%, 10%, ..., 99%)
    
    # Additional metrics
    probability_of_loss = Column(Float, nullable=True)  # Probability of any loss > 0
    exceedance_probabilities = Column(JSON, nullable=True)  # Loss exceedance curve data
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert simulation result to dictionary representation."""
        return {
            'id': str(self.id),
            'expected_loss': self.expected_loss,
            'var_95': self.var_95,
            'var_99': self.var_99,
            'var_99_9': self.var_99_9,
            'tvar_95': self.tvar_95,
            'tvar_99': self.tvar_99,
            'tvar_99_9': self.tvar_99_9,
            'min_loss': self.min_loss,
            'max_loss': self.max_loss,
            'std_deviation': self.std_deviation,
            'skewness': self.skewness,
            'kurtosis': self.kurtosis,
            'probability_of_loss': self.probability_of_loss,
            'loss_distribution': self.loss_distribution,
            'percentiles': self.percentiles,
            'exceedance_probabilities': self.exceedance_probabilities,
            'created_at': self.created_at.isoformat()
        }


class Scenario(db.Model):
    """Model for storing different simulation scenarios for comparison."""
    
    __tablename__ = 'scenarios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Base parameters
    base_parameters = Column(JSON, nullable=False)
    
    # Scenario modifications (multiplicative factors, additive changes, etc.)
    modifications = Column(JSON, nullable=False)
    
    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    simulation_runs = relationship('SimulationRun', backref='scenario', lazy='dynamic')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scenario to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'base_parameters': self.base_parameters,
            'modifications': self.modifications,
            'is_active': self.is_active,
            'simulation_count': self.simulation_runs.count(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class SystemConfiguration(db.Model):
    """Model for storing system-wide configuration settings."""
    
    __tablename__ = 'system_configurations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), 
                       onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary representation."""
        return {
            'id': str(self.id),
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Export all models for easy importing
__all__ = [
    'User',
    'Portfolio',
    'Policy',
    'SimulationRun',
    'SimulationResult',
    'Scenario',
    'SystemConfiguration'
] 