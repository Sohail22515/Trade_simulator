import os
import logging
import logging.config
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

def setup_logging(
    config_path: Optional[Path] = None,
    default_level: int = logging.INFO,
    env_key: Optional[str] = "TRADE_SIM_LOG_CFG"
) -> None:
    """Setup logging configuration from YAML file.
    
    Args:
        config_path: Explicit path to logging config
        default_level: Default logging level if config not found
        env_key: Environment variable name for config path override
    """
    # Check environment variable for config path
    if env_key and env_key in os.environ:
        config_path = Path(os.environ[env_key])
    elif config_path is None:
        config_path = Path(__file__).parent.parent / 'config' / 'logging_config.yaml'
    
    try:
        if config_path.exists():
            with open(config_path, 'rt', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config:
                    logging.config.dictConfig(config)
                    return
    except Exception as e:
        logging.warning(f"Failed to load logging config: {e}")
    
    logging.basicConfig(
        level=default_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logging.warning(f"Using basic logging config (failed to load from {config_path})")

def get_logger(name: str, extra: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """Get a configured logger instance with optional extra context.
    
    Args:
        name: Logger name (usually __name__)
        extra: Additional context for log records
    """
    logger = logging.getLogger(name)
    if extra:
        logger = logging.LoggerAdapter(logger, extra)
    return logger