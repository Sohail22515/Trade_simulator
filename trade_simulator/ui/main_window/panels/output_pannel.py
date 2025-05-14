from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from typing import Union
from trade_simulator.core.simulator import SimulationMetrics

class OutputPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._create_metrics_table()
        
    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Title
        self.title = QLabel("Trade Simulation Metrics")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title)
        
    def _create_metrics_table(self):
        """Create table for displaying metrics"""
        self.metrics_table = QTableWidget(6, 2)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.metrics_table.verticalHeader().setVisible(False)
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.metrics_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set up metric rows
        metrics = [
            ("Slippage", "0.00%"),
            ("Fees", "$0.00"),
            ("Market Impact", "0.00%"),
            ("Net Cost", "$0.00"),
            ("Maker/Taker Ratio", "0.00"),
            ("Processing Latency", "0.00ms")
        ]
        
        for row, (name, value) in enumerate(metrics):
            self.metrics_table.setItem(row, 0, QTableWidgetItem(name))
            self.metrics_table.setItem(row, 1, QTableWidgetItem(value))
        
        self.layout.addWidget(self.metrics_table)
    
    def update_metrics(self, metrics):
        """Update the displayed metrics"""
        if not metrics:
            return
        
        """Handle both dict and SimulationMetrics objects"""
        if hasattr(metrics, 'slippage'):  # It's a SimulationMetrics object
            self._update_metric(0, f"{metrics.slippage:.4f}%")
            self._update_metric(1, f"${metrics.fees:.4f}")
            self._update_metric(2, f"{metrics.total_impact:.4f}%")  # Changed from market_impact
            self._update_metric(3, f"${metrics.net_cost:.4f}")
            self._update_metric(4, f"{metrics.maker_taker_ratio:.2f}")
            self._update_metric(5, f"{metrics.latency_ms:.2f}ms")
        elif isinstance(metrics, dict):  # It's a dictionary
            self._update_metric(0, f"{metrics.get('slippage', 0):.4f}%")
            self._update_metric(1, f"${metrics.get('fees', 0):.4f}")
            self._update_metric(2, f"{metrics.get('market_impact', metrics.get('total_impact', 0)):.4f}%")  # Fallback
            self._update_metric(3, f"${metrics.get('net_cost', 0):.4f}")
            self._update_metric(4, f"{metrics.get('maker_taker', metrics.get('maker_taker_ratio', 0)):.2f}")
            self._update_metric(5, f"{metrics.get('latency', metrics.get('latency_ms', 0)):.2f}ms")
        
        # self._update_metric(0, f"{slippage:.4f}%")
        # self._update_metric(1, f"${fees:.4f}")
        # self._update_metric(2, f"{market_impact:.4f}%")
        # self._update_metric(3, f"${net_cost:.4f}")
        # self._update_metric(4, f"{maker_taker:.2f}")
        # self._update_metric(5, f"{latency:.2f}ms")
