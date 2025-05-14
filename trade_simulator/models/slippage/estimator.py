import numpy as np
from typing import Optional
from trade_simulator.utils.logging import get_logger
from trade_simulator.utils.exceptions import ModelError

class SlippageEstimator:
    """
    Estimates slippage for trades based on order book dynamics.
    Implements both immediate and time-weighted slippage models.
    """
    
    def __init__(self, window_size: int = 100, alpha: float = 0.2):
        """
        Args:
            window_size: Number of historical samples to maintain
            alpha: Smoothing factor for exponential weighting
        """
        self.logger = get_logger(__name__)
        self.window_size = window_size
        self.alpha = alpha
        self.historical_slippage = []
        
    def estimate(self, order_book, quantity: float, model: str = 'linear') -> float:
        """
        Estimate slippage for a given trade quantity.
        
        Args:
            order_book: Current order book state
            quantity: Trade quantity in base asset units
            model: Estimation model ('linear', 'exponential', 'quantile')
            
        Returns:
            Estimated slippage as a percentage of mid-price
        """
        try:
            if not hasattr(order_book, 'asks') or not hasattr(order_book, 'bids'):
                raise ModelError("Invalid order book structure")
                
            if quantity <= 0:
                return 0.0
                
            mid_price = (order_book.asks[0][0] + order_book.bids[0][0]) / 2
            if mid_price <= 0:
                raise ModelError("Invalid mid price")
                
            if model == 'linear':
                return self._linear_model(order_book, quantity, mid_price)
            elif model == 'exponential':
                return self._exponential_model(order_book, quantity, mid_price)
            elif model == 'quantile':
                return self._quantile_model(order_book, quantity, mid_price)
            else:
                raise ModelError(f"Unknown slippage model: {model}")
                
        except Exception as e:
            self.logger.error(f"Slippage estimation failed: {e}")
            raise ModelError(f"Slippage estimation error: {e}") from e
            
    def _linear_model(self, order_book, quantity: float, mid_price: float) -> float:
        """Linear slippage model based on order book depth"""
        remaining = quantity
        total_cost = 0.0
        
        for price, amount in order_book.asks:
            if remaining <= 0:
                break
            fill = min(amount, remaining)
            total_cost += price * fill
            remaining -= fill
            
        if quantity == 0:
            return 0.0
            
        avg_price = total_cost / quantity
        return (avg_price - mid_price) / mid_price
        
    def _exponential_model(self, order_book, quantity: float, mid_price: float) -> float:
        """Exponentially weighted slippage model"""
        remaining = quantity
        total_cost = 0.0
        weight_sum = 0.0
        depth = 0
        
        for price, amount in order_book.asks:
            if remaining <= 0:
                break
            fill = min(amount, remaining)
            weight = np.exp(-self.alpha * depth)
            total_cost += price * fill * weight
            weight_sum += fill * weight
            remaining -= fill
            depth += 1
            
        if weight_sum == 0:
            return 0.0
            
        avg_price = total_cost / weight_sum
        return (avg_price - mid_price) / mid_price
        
    def _quantile_model(self, order_book, quantity: float, mid_price: float) -> float:
        """Quantile-based conservative slippage estimate"""
        if len(self.historical_slippage) >= self.window_size:
            self.historical_slippage.pop(0)
            
        linear_slip = self._linear_model(order_book, quantity, mid_price)
        exp_slip = self._exponential_model(order_book, quantity, mid_price)
        
        current_estimate = max(linear_slip, exp_slip)
        self.historical_slippage.append(current_estimate)
        
        if len(self.historical_slippage) < 10:  # Minimum samples
            return current_estimate
            
        return np.quantile(self.historical_slippage, 0.9)  # 90th percentile
        
    def update_model(self, actual_slippage: float):
        """Update model with actual observed slippage"""
        if len(self.historical_slippage) >= self.window_size:
            self.historical_slippage.pop(0)
        self.historical_slippage.append(actual_slippage)