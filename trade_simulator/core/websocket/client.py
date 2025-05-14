import asyncio
import websockets
import json
import logging
from typing import Callable, Optional
from dataclasses import dataclass
from trade_simulator.utils.exceptions import WebSocketError  # Absolute import
from trade_simulator.core.orderbook.book import OrderBook  # Absolute import

@dataclass
class WSConfig:
    url: str
    reconnect_delay: int = 5
    max_retries: Optional[int] = None

class WebSocketClient:
    def __init__(
        self,
        config: WSConfig,
        message_handler: Callable,
        logger: Optional[logging.Logger] = None
    ):
        self.config = config
        self.message_handler = message_handler
        self.logger = logger or logging.getLogger(__name__)
        self._is_running = False
        self._retry_count = 0
        
    async def connect(self):
        self._is_running = True
        while self._is_running:
            try:
                async with websockets.connect(self.config.url) as ws:
                    self.logger.info(f"WebSocket connected to {self.config.url}")
                    self._retry_count = 0
                    await self._listen(ws)
                    
            except websockets.exceptions.ConnectionClosed as e:
                self.logger.warning(f"Connection closed: {e}, reconnecting...")
            except Exception as e:
                self.logger.error(f"WebSocket error: {str(e)}", exc_info=True)
                
            if self.config.max_retries and self._retry_count >= self.config.max_retries:
                self.logger.error("Max retries reached, stopping WebSocket")
                break
                
            await asyncio.sleep(self.config.reconnect_delay)
            self._retry_count += 1
            
    async def _listen(self, websocket):
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.message_handler(data)
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error: {e}")
                except Exception as e:
                    self.logger.error(f"Message processing error: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Listen error: {e}", exc_info=True)
            raise WebSocketError(f"Listen error: {str(e)}") from e
            
    async def stop(self):
        self._is_running = False