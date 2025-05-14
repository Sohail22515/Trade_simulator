import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStatusBar, QLabel
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject
from trade_simulator.ui.resources.stylesheet import load_stylesheet
from trade_simulator.ui.main_window.panels.input_pannel import InputPanel
from trade_simulator.ui.main_window.panels.output_pannel import OutputPanel
from trade_simulator.core.simulator import SimulationMetrics
from trade_simulator.utils.logging import get_logger

class MainWindow(QMainWindow):
    # update_ui_signal = pyqtSignal(dict)
    update_ui_signal = pyqtSignal(SimulationMetrics)
    
    def __init__(self, simulator: SimulationMetrics):
        super().__init__()
        self.simulator = simulator
        self.logger = get_logger(__name__)
        self._init_ui()
        self._setup_signals()
        self._setup_timer()
        self._init_connection_status()

    def _init_connection_status(self):
        """Initialize the connection status indicator"""
        self.connection_status = QLabel("Connecting...")
        self.connection_status.setStyleSheet("color: orange; font-weight: bold;")
        self.statusBar().addPermanentWidget(self.connection_status)
        
        # Safe signal connection
        try:
            if isinstance(self.simulator, QObject):  # Check if it's a Qt object
                self.simulator.connection_signal.connect(self._update_connection_status)
        except Exception as e:
            print(f"Could not connect signals: {e}")

    def _update_connection_status(self, is_connected: bool):
        """Update the connection status display"""
        status = "Connected" if is_connected else "Disconnected"
        color = "green" if is_connected else "red"
        
        self.connection_status.setText(status)
        self.connection_status.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                padding: 2px 5px;
            }}
        """)

    def _init_ui(self):
        """Initialize all UI components"""
        self.setWindowTitle("Crypto Trade Simulator")
        self.setMinimumSize(1000, 700)
        
        # Load stylesheet
        try:
            self.setStyleSheet(load_stylesheet())
        except Exception as e:
            self.logger.warning(f"Could not load stylesheet: {e}")
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        central_widget.setLayout(main_layout)
        
        # Input panel (left)
        self.input_panel = InputPanel(self.simulator)
        main_layout.addWidget(self.input_panel, 1)
        
        # Output panel (right)
        self.output_panel = OutputPanel()
        main_layout.addWidget(self.output_panel, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready", 3000)

    def _setup_signals(self):
        """Connect all signals and slots"""
        self.update_ui_signal.connect(self._update_ui)
        
        # Connect input panel signals if available
        if hasattr(self.input_panel, 'parameters_changed'):
            self.input_panel.parameters_changed.connect(self._on_parameters_changed)
        else:
            self.logger.warning("InputPanel is missing parameters_changed signal")

    def _setup_timer(self):
        """Set up UI refresh timer"""
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._refresh_ui)
        
        # Get update interval from settings or use default
        try:
            interval = getattr(self.simulator, 'settings', {}).get('UI_UPDATE_INTERVAL', 500)
        except Exception as e:
            self.logger.error(f"Could not get UI update interval: {e}")
            interval = 500  # Default 500ms interval
            
        self.ui_timer.start(interval)

    def _refresh_ui(self):
        """Refresh UI with current metrics"""
        try:
            if not self.simulator._running or not self.simulator._order_book:
                return
                
            metrics = self.simulator.get_current_metrics()
            self.update_ui_signal.emit(metrics)
        except Exception as e:
            self.logger.error(f"UI refresh error: {e}", exc_info=True)
            self.status_bar.showMessage(f"Error: {str(e)}", 3000)

    def _update_ui(self, metrics: SimulationMetrics):
        """Update UI with new metrics"""
        try:
            self.output_panel.update_metrics({
                'slippage': metrics.slippage,
                'fees': metrics.fees,
                'market_impact': metrics.market_impact,
                'net_cost': metrics.net_cost,
                'maker_taker': metrics.maker_taker_ratio,
                'latency': metrics.latency_ms
            })
                
        except Exception as e:
            self.logger.error(f"Output panel update failed: {e}", exc_info=True)

    def _on_parameters_changed(self, params: dict):
        """Handle parameter changes from input panel"""
        try:
            self.simulator.update_parameters(params)
            self.status_bar.showMessage("Parameters updated successfully", 3000)
        except Exception as e:
            self.logger.error(f"Parameter update error: {e}", exc_info=True)
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            if hasattr(self.simulator, 'stop'):
                self.simulator.stop()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
        finally:
            super().closeEvent(event)