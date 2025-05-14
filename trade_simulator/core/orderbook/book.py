import numpy as np
from datetime import datetime
from typing import List, Tuple, Optional
from trade_simulator.utils.exceptions import OrderBookError  # Absolute import

class OrderBook:
    def __init__(self, symbol: str, max_depth: int = 1000):
        self.symbol = symbol
        self.max_depth = max_depth
        self.bids = np.zeros((0, 2), dtype='float64')
        self.asks = np.zeros((0, 2), dtype='float64')
        self.timestamp: Optional[datetime] = None
        self._sequence_id = 0
        
    def update_book(self, data: dict) -> None:
        """Update order book with new data"""
        try:
            self.timestamp = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%SZ")
            self._sequence_id += 1
            
            # Process bids
            self.bids = self._process_levels(data['bids'], ascending=False)
            
            # Process asks
            self.asks = self._process_levels(data['asks'], ascending=True)
            
        except (KeyError, ValueError, TypeError) as e:
            raise OrderBookError(f"Invalid order book data: {str(e)}") from e
            
    def _process_levels(self, levels: List[List[str]], ascending: bool) -> np.ndarray:
        """Convert and sort price levels"""
        arr = np.array(
            [[float(price), float(amount)] for price, amount in levels],
            dtype='float64'
        )
        return self._sort_and_limit(arr, ascending)
            
    def _sort_and_limit(self, levels: np.ndarray, ascending: bool) -> np.ndarray:
        """Sort and limit order book levels"""
        if levels.size == 0:
            return levels
            
        # Sort by price
        sorted_levels = levels[levels[:, 0].argsort()]
        if not ascending:
            sorted_levels = np.flipud(sorted_levels)
            
        # Limit depth
        return sorted_levels[:self.max_depth]
        
    def get_mid_price(self) -> float:
        """Calculate current mid price"""
        if self.bids.size == 0 or self.asks.size == 0:
            raise OrderBookError("Cannot calculate mid price - empty order book")
        return (self.bids[0][0] + self.asks[0][0]) / 2
        
    def get_spread(self) -> float:
        """Calculate current bid-ask spread"""
        if self.bids.size == 0 or self.asks.size == 0:
            raise OrderBookError("Cannot calculate spread - empty order book")
        return self.asks[0][0] - self.bids[0][0]
        
    def get_total_volume(self) -> float:
        """Calculate total volume available in order book"""
        return np.sum(self.asks[:, 1]) + np.sum(self.bids[:, 1])