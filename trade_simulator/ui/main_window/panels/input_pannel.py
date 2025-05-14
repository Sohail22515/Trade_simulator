from PyQt5.QtGui import QDoubleValidator, QIcon, QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QFormLayout, QFrame, QSizePolicy
)
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Dict, Any

class InputPanel(QWidget):
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self.setObjectName("InputPanel")
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the modern UI layout with better visual hierarchy"""
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)
        
        # Panel title
        title = QLabel("Trade Parameters")
        title.setObjectName("PanelTitle")
        main_layout.addWidget(title)
        
        # Form for parameters
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(15)
        
        # Exchange Selection with icon
        exchange_layout = QHBoxLayout()
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["OKX", "Binance", "Kraken"])
        exchange_layout.addWidget(self.exchange_combo)
        form_layout.addRow(QLabel("Exchange:"), self.exchange_combo)
        
        # Asset Selection
        self.asset_combo = QComboBox()
        self.asset_combo.addItems(["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "ADA-USDT"])
        form_layout.addRow(QLabel("Asset:"), self.asset_combo)
        
        # Quantity Input
        self.quantity_input = QLineEdit("100")
        self.quantity_input.setValidator(QDoubleValidator(0.01, 1000000, 2))
        self.quantity_input.setPlaceholderText("Enter amount...")
        form_layout.addRow(QLabel("Quantity (USD):"), self.quantity_input)
        
        # Order Type
        self.order_type_combo = QComboBox()
        self.order_type_combo.addItems(["Market", "Limit", "Stop-Limit"])
        form_layout.addRow(QLabel("Order Type:"), self.order_type_combo)
        
        # Fee Tier
        self.fee_tier_combo = QComboBox()
        self.fee_tier_combo.addItems(["1", "2", "3", "4"])
        form_layout.addRow(QLabel("Fee Tier:"), self.fee_tier_combo)
        
        # Add limit price input - only shown when appropriate
        self.limit_price_input = QLineEdit()
        self.limit_price_input.setValidator(QDoubleValidator(0.01, 1000000, 2))
        self.limit_price_input.setPlaceholderText("Enter limit price...")
        self.limit_price_label = QLabel("Limit Price:")
        self.limit_price_input.hide()
        self.limit_price_label.hide()
        form_layout.addRow(self.limit_price_label, self.limit_price_input)
        
        # Connect order type to show/hide limit price
        self.order_type_combo.currentTextChanged.connect(self._update_limit_visibility)
        
        # Add form to main layout
        main_layout.addLayout(form_layout)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        main_layout.addWidget(spacer)
        
        # Action Buttons in horizontal layout
        button_layout = QHBoxLayout()
        
        # Reset Button
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self._reset_form)
        
        # Submit Button
        self.submit_btn = QPushButton("Update Parameters")
        self.submit_btn.clicked.connect(self._on_submit)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.submit_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def _update_limit_visibility(self, order_type):
        """Show/hide limit price input based on order type"""
        show_limit = order_type in ["Limit", "Stop-Limit"]
        self.limit_price_input.setVisible(show_limit)
        self.limit_price_label.setVisible(show_limit)
    
    def _reset_form(self):
        """Reset all form fields to defaults"""
        self.exchange_combo.setCurrentIndex(0)
        self.asset_combo.setCurrentIndex(0)
        self.quantity_input.setText("100")
        self.order_type_combo.setCurrentIndex(0)
        self.fee_tier_combo.setCurrentIndex(0)
        self.limit_price_input.clear()
    
    def _on_submit(self):
        """Collect all parameters and emit them"""
        params = {
            'exchange': self.exchange_combo.currentText(),
            'symbol': self.asset_combo.currentText(),
            'quantity_usd': float(self.quantity_input.text() or "0"),
            'order_type': self.order_type_combo.currentText().lower(),
            'fee_tier': int(self.fee_tier_combo.currentText())
        }
        
        # Add limit price if visible
        if self.limit_price_input.isVisible() and self.limit_price_input.text():
            params['limit_price'] = float(self.limit_price_input.text())
        
        self.parameters_changed.emit(params)