"""
Custom exceptions for the simulation engine.
"""


class SimulationError(Exception):
    """Base exception for simulation-related errors."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_dict(self):
        """Convert exception to dictionary representation."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details
        }


class ParameterError(SimulationError):
    """Exception raised for invalid simulation parameters."""
    pass


class DistributionError(SimulationError):
    """Exception raised for distribution-related errors."""
    pass


class FinancialCalculationError(SimulationError):
    """Exception raised for financial calculation errors."""
    pass


class ConvergenceError(SimulationError):
    """Exception raised when simulation fails to converge."""
    pass


class ValidationError(SimulationError):
    """Exception raised when input validation fails."""
    pass 