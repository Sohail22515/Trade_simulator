import numpy as np
from dataclasses import dataclass
from typing import Optional
from trade_simulator.utils.logging import get_logger
from trade_simulator.utils.exceptions import ModelError

@dataclass
class MarketImpactResult:
    """Container for market impact calculation results"""
    permanent_impact: float
    temporary_impact: float
    total_impact: float
    optimal_execution_time: float

class AlmgrenChrissModel:
    """
    Implementation of the Almgren-Chriss market impact model for optimal trade execution.
    
    The model calculates:
    - Permanent impact (information leakage)
    - Temporary impact (liquidity demand)
    - Optimal execution strategy
    """
    
    def __init__(self, 
                 eta: float = 0.1, 
                 gamma: float = 0.01,
                 sigma: Optional[float] = None,
                 risk_aversion: float = 1e-6):
        """
        Args:
            eta: Permanent impact coefficient (default 0.1)
            gamma: Temporary impact coefficient (default 0.01)
            sigma: Volatility (annualized). If None, will use recent realized vol.
            risk_aversion: Trader's risk aversion parameter (default 1e-6)
        """
        self.logger = get_logger(__name__)
        self.eta = eta
        self.gamma = gamma
        self.sigma = sigma
        self.risk_aversion = risk_aversion
        self.price_history = []
        
    def calculate_impact(self,
                       quantity: float,
                       total_volume: float,
                       volatility: Optional[float] = None,
                       time_horizon: Optional[float] = None) -> MarketImpactResult:
        """
        Calculate market impact for a given trade size.
        
        Args:
            quantity: Order quantity in shares/units
            total_volume: Total market volume (for normalization)
            volatility: Current volatility estimate (optional)
            time_horizon: Execution time horizon in days (optional)
            
        Returns:
            MarketImpactResult with components and optimal execution time
        """
        try:
            # Input validation
            if quantity <= 0 or total_volume <= 0:
                return MarketImpactResult(0, 0, 0, 0)
                
            if volatility is None:
                volatility = self.sigma or self._estimate_volatility()
                
            if volatility <= 0:
                raise ModelError("Volatility must be positive")
                
            # Normalized order size
            x = quantity / total_volume
            
            # Permanent impact (linear in order size)
            permanent_impact = self.eta * volatility * x
            
            # Calculate optimal execution time if not provided
            if time_horizon is None:
                time_horizon = self._optimal_execution_time(
                    quantity, total_volume, volatility
                )
            
            # Temporary impact (depends on execution speed)
            temporary_impact = self.gamma * volatility * x / time_horizon
            
            return MarketImpactResult(
                permanent_impact=permanent_impact,
                temporary_impact=temporary_impact,
                total_impact=permanent_impact + temporary_impact,
                optimal_execution_time=time_horizon
            )
            
        except Exception as e:
            self.logger.error(f"Market impact calculation failed: {e}")
            raise ModelError(f"Market impact error: {e}") from e
            
    def _optimal_execution_time(self,
                              quantity: float,
                              total_volume: float,
                              volatility: float) -> float:
        """
        Calculate optimal execution time (T) using Almgren-Chriss formula:
        T = (3γX^2 / 2ησ^2κ)^(1/3)
        """
        x = quantity / total_volume
        numerator = 3 * self.gamma * x**2
        denominator = 2 * self.eta * volatility**2 * self.risk_aversion
        return (numerator / denominator) ** (1/3)
        
    def update_volatility_estimate(self, new_price: float):
        """Update volatility estimate with latest price"""
        self.price_history.append(new_price)
        if len(self.price_history) > 100:  # Keep last 100 prices
            self.price_history.pop(0)
            
    def _estimate_volatility(self) -> float:
        """Estimate volatility from price history"""
        if len(self.price_history) < 2:
            return 0.02  # Default 2% volatility
            
        returns = np.diff(np.log(self.price_history))
        return np.std(returns) * np.sqrt(252)  # Annualized