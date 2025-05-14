import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStatusBar, QLabel, QFrame, QSplitter, QToolBar,
    QAction, QMenu, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QObject, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont
from trade_simulator.ui.resources.stylesheet import load_stylesheet
from trade_simulator.ui.main_window.panels.input_pannel import InputPanel
from trade_simulator.ui.main_window.panels.output_pannel import OutputPanel
from trade_simulator.core.simulator import SimulationMetrics
from trade_simulator.utils.logging import get_logger

class MainWindow(QMainWindow):
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
        self.connection_status.setObjectName("StatusConnecting")
        self.statusBar().addPermanentWidget(self.connection_status)
        
        # Safe signal connection
        try:
            if isinstance(self.simulator, QObject):  # Check if it's a Qt object
                self.simulator.connection_signal.connect(self._update_connection_status)
        except Exception as e:
            self.logger.error(f"Could not connect signals: {e}")

    def _update_connection_status(self, is_connected: bool):
        """Update the connection status display"""
        if is_connected:
            status = "Connected"
            self.connection_status.setObjectName("StatusConnected")
        else:
            status = "Disconnected"
            self.connection_status.setObjectName("StatusDisconnected")
        
        self.connection_status.setText(status)
        
        # Force style refresh
        self.connection_status.style().unpolish(self.connection_status)
        self.connection_status.style().polish(self.connection_status)

    def _init_ui(self):
        """Initialize all UI components with modern design"""
        self.setWindowTitle("Crypto Trade Simulator")
        self.setMinimumSize(1200, 800)
        
        # Load stylesheet
        try:
            self.setStyleSheet(load_stylesheet())
        except Exception as e:
            self.logger.warning(f"Could not load stylesheet: {e}")
        
        # Create toolbar with actions
        self._create_toolbar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter for responsiveness
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create splitter for responsive resizing
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(2)
        self.splitter.setChildrenCollapsible(False)
        
        # Input panel (left)
        self.input_panel = InputPanel(self.simulator)
        self.splitter.addWidget(self.input_panel)
        
        # Output panel (right)
        self.output_panel = OutputPanel()
        self.splitter.addWidget(self.output_panel)
        
        # Set initial sizes (40% input, 60% output)
        self.splitter.setSizes([400, 600])
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
        
        # Status bar with modern styling
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add app name to status bar
        app_name = QLabel("Crypto Trade Simulator")
        app_name.setStyleSheet("font-weight: bold;")
        self.status_bar.addWidget(app_name)
        
        # Add version info
        version_info = QLabel("v1.0.0")
        self.status_bar.addWidget(version_info)
        
        # Initial status message
        self.status_bar.showMessage("Ready", 3000)

    def _create_toolbar(self):
        """Create a modern toolbar with actions"""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setStyleSheet("""
            QToolBar {
                spacing: 10px;
                background-color: #272736;
                border-bottom: 1px solid #3a3a4a;
            }
            
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            
            QToolButton:hover {
                background-color: #3a3a4a;
            }
            
            QToolButton:pressed {
                background-color: #5294e2;
            }
        """)
        
        # Add actions - using text since we don't have icons
        start_action = QAction("Start", self)
        start_action.triggered.connect(self._start_simulation)
        self.toolbar.addAction(start_action)
        
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self._stop_simulation)
        self.toolbar.addAction(stop_action)
        
        self.toolbar.addSeparator()
        
        layout_action = QAction("Toggle Layout", self)
        layout_action.triggered.connect(self._toggle_layout)
        self.toolbar.addAction(layout_action)
        
        theme_action = QAction("Toggle Theme", self)
        theme_action.triggered.connect(self._toggle_theme)
        self.toolbar.addAction(theme_action)
        
        self.toolbar.addSeparator()
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        self.toolbar.addAction(about_action)
        
        self.addToolBar(self.toolbar)

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

    def _start_simulation(self):
        """Start the simulation"""
        try:
            if hasattr(self.simulator, 'start'):
                self.simulator.start()
                self.status_bar.showMessage("Simulation started", 3000)
        except Exception as e:
            self.logger.error(f"Failed to start simulation: {e}", exc_info=True)
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)

    def _stop_simulation(self):
        """Stop the simulation"""
        try:
            if hasattr(self.simulator, 'stop'):
                self.simulator.stop()
                self.status_bar.showMessage("Simulation stopped", 3000)
        except Exception as e:
            self.logger.error(f"Failed to stop simulation: {e}", exc_info=True)
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)

    def _toggle_layout(self):
        """Toggle between horizontal and vertical layout"""
        if self.splitter.orientation() == Qt.Horizontal:
            self.splitter.setOrientation(Qt.Vertical)
        else:
            self.splitter.setOrientation(Qt.Horizontal)

    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        # This is a placeholder as we'd need to implement theme switching
        # For now, just show a message
        self.status_bar.showMessage("Theme switching not implemented yet", 3000)

    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Crypto Trade Simulator", 
                         """<h3>Crypto Trade Simulator</h3>
                         <p>A modern tool for simulating cryptocurrency trades and analyzing costs.</p>
                         <p>Version 1.0.0</p>""")

    def _refresh_ui(self):
        """Refresh UI with current metrics"""
        try:
            if not hasattr(self.simulator, '_running') or not self.simulator._running:
                return
                
            if not hasattr(self.simulator, '_order_book') or not self.simulator._order_book:
                return
                
            metrics = self.simulator.get_current_metrics()
            self.update_ui_signal.emit(metrics)
        except Exception as e:
            self.logger.error(f"UI refresh error: {e}", exc_info=True)
            self.status_bar.showMessage(f"Error: {str(e)}", 3000)

    def _update_ui(self, metrics: SimulationMetrics):
        """Update UI with new metrics"""
        try:
            # Update output panel
            self.output_panel.update_metrics(metrics)
                
        except Exception as e:
            self.logger.error(f"Output panel update failed: {e}", exc_info=True)

    def _on_parameters_changed(self, params: dict):
        """Handle parameter changes from input panel"""
        try:
            if hasattr(self.simulator, 'update_parameters'):
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