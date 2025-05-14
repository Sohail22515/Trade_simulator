import asyncio
import logging
import time 
from typing import Dict, Any
from dataclasses import dataclass
from trade_simulator.core.websocket.client import WebSocketClient, WSConfig
from trade_simulator.core.orderbook.book import OrderBook
from trade_simulator.models.slippage.estimator import SlippageEstimator
from trade_simulator.models.market_impact.almgren_chriss import AlmgrenChrissModel
from trade_simulator.models.fees.calculator import FeeCalculator
from trade_simulator.utils.exceptions import TradeSimulatorError
from trade_simulator.config.settings import settings
from PyQt5.QtCore import QObject, pyqtSignal

@dataclass
class SimulationMetrics:
    slippage: float
    fees: float
    market_impact: float
    net_cost: float
    maker_taker_ratio: float
    latency_ms: float

class TradeSimulator(QObject):

    connection_signal = pyqtSignal(bool)
    
    async def _process_message(self, message: Dict[str, Any]):
        try:
            if not hasattr(self, '_order_book'):
                self._order_book = OrderBook(self._params['symbol'])
                self.connection_signal.emit(True)  # Notify UI
            # ... rest of your processing code ...
        except Exception as e:
            self.connection_signal.emit(False)
            raise
        
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._order_book = None
        self._ws_client = None
        self._ws_task = None
        
        # Initialize models
        self.slippage_model = SlippageEstimator()
        self.impact_model = AlmgrenChrissModel()
        self.fee_model = FeeCalculator()
        
        # Simulation parameters
        self._params = {
            'exchange': 'OKX',
            'symbol': 'BTC-USDT-SWAP',
            'quantity_usd': 100.0,
            'volatility': 0.02,
            'fee_tier': 1
        }
        
    async def start(self):
        """Initialize and start the simulator"""
        if self._running:
            raise TradeSimulatorError("Simulator already running")
            
        self._running = True
        self._order_book = OrderBook(self._params['symbol'])
        
        # Setup WebSocket
        ws_config = WSConfig(
            url=settings.WS_URL,
            reconnect_delay=settings.WS_RECONNECT_DELAY
        )
        # self._ws_client = WebSocketClient(
        #     config=ws_config,
        #     message_handler=self._process_message
        # )
        self._ws_client = WebSocketClient(ws_config, self._process_message)

        # Start WebSocket in background
        self._ws_task = asyncio.create_task(self._ws_client.connect())

        await self._wait_for_initial_data()
    
    async def _wait_for_initial_data(self, timeout=10):
        """Wait until order book receives first update"""
        start = time.time()
        while not self._order_book.timestamp:
            if time.time() - start > timeout:
                raise TradeSimulatorError("Order book initialization timeout")
            await asyncio.sleep(0.1)
        
    def stop(self):
            if not self._running:
                return
                
            self._running = False
            if hasattr(self, '_ws_task') and self._ws_task:
                self._ws_task.cancel()
            
    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming WebSocket messages"""
        try:
            self._order_book.update_book(message)
            # Additional processing can be added here
        except Exception as e:
            self.logger.error(f"Message processing failed: {e}", exc_info=True)
            
    def get_current_metrics(self) -> SimulationMetrics:
        """Calculate all current metrics"""
        if not self._order_book:
            raise TradeSimulatorError("Order book not initialized")
            
        try:
            quantity = self._calculate_quantity()
            
            slippage = self.slippage_model.estimate(
                self._order_book, 
                quantity
            )
            
            fees = self.fee_model.calculate(
                quantity,
                str(self._params.get('exchange', 'OKX')),  # Ensure string
                self._params.get('fee_tier', 1),
                # is_maker_order
            )
            
            impact = self.impact_model.calculate_impact(
                quantity,
                self._order_book.get_total_volume(),
                self._params['volatility']
            )
            
            return SimulationMetrics(
                slippage=slippage,
                fees=fees,
                market_impact=impact.total_impact,
                net_cost=slippage + fees + impact.total_impact,
                maker_taker_ratio=self._estimate_maker_taker(),
                latency_ms=self._calculate_latency()
            )
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {e}", exc_info=True)
            raise TradeSimulatorError(f"Metrics calculation failed: {e}") from e
            
    def _calculate_quantity(self) -> float:
        """Convert USD quantity to base asset units"""
        mid_price = self._order_book.get_mid_price()
        return self._params['quantity_usd'] / mid_price
        
    def _estimate_maker_taker(self) -> float:
        """Placeholder for maker/taker ratio estimation"""
        # Implement actual logic based on order book analysis
        return 0.7  # Example value
        
    def _calculate_latency(self) -> float:
        """Calculate processing latency"""
        # Implement actual latency measurement
        return 5.0  # Example value in ms
        
    def update_parameters(self, params: Dict[str, Any]):
        """Update simulation parameters"""
        self._params.update(params)
        self.logger.info("Parameters updated: %s", self._params)