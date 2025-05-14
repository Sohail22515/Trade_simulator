import sys
import signal
import asyncio
import logging
from PyQt5.QtWidgets import QApplication
from trade_simulator.core.simulator import TradeSimulator
from trade_simulator.ui.main_window.window import MainWindow
from trade_simulator.utils.logging import setup_logging
from trade_simulator.utils.exceptions import handle_uncaught_exceptions

def handle_signals(app):
    """Make Ctrl+C work properly with Qt"""
    signal.signal(signal.SIGINT, lambda *args: app.quit())
    signal.signal(signal.SIGTERM, lambda *args: app.quit())

async def run_app():
    """Async application entry point"""
    # Configure logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing Trade Simulator")
        
        # Create simulator instance
        simulator = TradeSimulator()
        
        # Initialize Qt application
        app = QApplication(sys.argv)
        handle_signals(app)
        
        # Setup main window
        window = MainWindow(simulator)
        window.show()
        
        # Start simulator
        await simulator.start()
        
        logger.info("Application started successfully")
        return app.exec_()
        
    except ImportError as e:
        logger.critical(f"Import error: {e}", exc_info=True)
        print(f"Fatal import error: {e}. Check your installation.", file=sys.stderr)
        return 1
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1
    finally:
        if 'simulator' in locals():
            simulator.stop()
        logger.info("Application shutdown complete")

def main() -> int:
    """Main entry point that handles async/sync bridge"""
    # Setup global error handling
    sys.excepthook = handle_uncaught_exceptions
    
    # Configure asyncio for Windows if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        return asyncio.run(run_app())
    except KeyboardInterrupt:
        print("\nApplication terminated by user", file=sys.stderr)
        return 0

if __name__ == "__main__":
    sys.exit(main())