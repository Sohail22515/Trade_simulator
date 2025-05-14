from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFormLayout
)
from PyQt5.QtCore import pyqtSignal
from typing import Dict, Any

class InputPanel(QWidget):
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self._init_ui()
        
    def _init_ui(self):
        layout = QFormLayout()
        
        # Exchange Selection
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["OKX", "Binance", "Kraken"])
        layout.addRow("Exchange:", self.exchange_combo)
        
        # Asset Selection
        self.asset_combo = QComboBox()
        self.asset_combo.addItems(["BTC-USDT", "ETH-USDT", "SOL-USDT"])
        layout.addRow("Asset:", self.asset_combo)
        
        # Quantity Input
        self.quantity_input = QLineEdit("100")
        self.quantity_input.setValidator(QDoubleValidator(0.01, 1000000, 2))
        layout.addRow("Quantity (USD):", self.quantity_input)
        
        # Order Type
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Market", "Limit"])
        layout.addRow("Order Type:", self.order_type_combo)
        
        # Fee Tier
        self.fee_tier_combo = QComboBox()
        self.fee_tier_combo.addItems(["1", "2", "3", "4"])
        layout.addRow("Fee Tier:", self.fee_tier_combo)
        
        # Submit Button
        self.submit_btn = QPushButton("Update Parameters")
        self.submit_btn.clicked.connect(self._on_submit)
        layout.addRow(self.submit_btn)
        
        self.setLayout(layout)
    
    def _on_submit(self):
        """Collect all parameters and emit them"""
        params = {
            'exchange': self.exchange_combo.currentText(),
            'symbol': self.asset_combo.currentText(),
            'quantity_usd': float(self.quantity_input.text()),
            'order_type': self.order_type_combo.currentText().lower(),
            'fee_tier': int(self.fee_tier_combo.currentText())
        }
        self.parameters_changed.emit(params)