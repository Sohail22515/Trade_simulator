import sys
import traceback
from typing import Callable, Type, Union

def handle_uncaught_exceptions(exc_type: Type[BaseException], 
                              exc_value: BaseException, 
                              exc_traceback) -> None:
    """
    Global exception handler for uncaught exceptions.
    Logs the error and shows a user-friendly message.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Format the error message
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Log the error (you could use logging module here)
    print(f"Uncaught exception:\n{error_msg}", file=sys.stderr)
    
    # Here you could also show a QMessageBox if using PyQt
    # from PyQt5.QtWidgets import QMessageBox
    # QMessageBox.critical(None, "Error", f"An error occurred:\n{str(exc_value)}")


class TradeSimulatorError(Exception):
    """Base exception for the application"""
    pass

class WebSocketError(TradeSimulatorError):
    """WebSocket related errors"""
    pass

class OrderBookError(TradeSimulatorError):
    """Order book processing errors"""
    pass

class ModelError(TradeSimulatorError):
    """Model calculation errors"""
    pass

class UIError(TradeSimulatorError):
    """User interface errors"""
    pass

class ConfigurationError(TradeSimulatorError):
    """Configuration related errors"""
    pass