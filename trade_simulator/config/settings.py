import os
import yaml
from pathlib import Path
from typing import Dict, Any
from trade_simulator.utils.logging import get_logger

logger = get_logger(__name__)

class Settings:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent
        self._settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        config_path = self.BASE_DIR / 'config' / 'app_config.yaml'
        default_settings = {
            'websocket': {
                'url': 'wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP',
                'reconnect_delay': 5
            },
            'app': {
                'ui_update_interval_ms': 100
            },
            'exchanges': {}
        }
        
        try:
            if config_path.exists():
                with open(config_path) as f:
                    return yaml.safe_load(f) or default_settings
            logger.warning(f"Config file not found at {config_path}, using defaults")
            return default_settings
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return default_settings
        
    @property
    def WS_URL(self) -> str:
        return self._settings['websocket']['url']
        
    @property
    def WS_RECONNECT_DELAY(self) -> int:
        return self._settings['websocket']['reconnect_delay']
        
    @property
    def UI_UPDATE_INTERVAL(self) -> int:
        return self._settings['app']['ui_update_interval_ms']
        
    def get_exchange_config(self, exchange: str) -> Dict[str, Any]:
        return self._settings['exchanges'].get(exchange.upper(), {})

settings = Settings()