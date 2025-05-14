from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout,
    QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette
from typing import Union, Dict, Optional

class MetricCard(QFrame):
    """A modern card widget for displaying a single metric with improved styling"""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("MetricCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumSize(150, 100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Styling
        self.setStyleSheet("""
            #MetricCard {
                background: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            .MetricValue {
                font-size: 20px;
                font-weight: 600;
                color: #333333;
            }
            .MetricName {
                font-size: 14px;
                color: #666666;
            }
            .MetricValue[valueType="positive"] {
                color: #4CAF50;
            }
            .MetricValue[valueType="negative"] {
                color: #F44336;
            }
        """)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "MetricName")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Value
        self.value_label = QLabel("--")
        self.value_label.setProperty("class", "MetricValue")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Optional description
        self.desc_label = QLabel()
        self.desc_label.setProperty("class", "MetricDesc")
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setVisible(False)
        layout.addWidget(self.desc_label)
        
        self.setLayout(layout)
    
    def update_value(self, value: str, is_positive: Optional[bool] = None, description: str = ""):
        """Update the displayed value with optional styling and description"""
        self.value_label.setText(value)
        
        # Apply color based on positive/negative value if specified
        if is_positive is not None:
            value_type = "positive" if is_positive else "negative"
            self.value_label.setProperty("valueType", value_type)
            self.value_label.style().unpolish(self.value_label)
            self.value_label.style().polish(self.value_label)
        
        # Update description if provided
        if description:
            self.desc_label.setText(description)
            self.desc_label.setVisible(True)
        else:
            self.desc_label.setVisible(False)


class OutputPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("OutputPanel")
        self._init_ui()
        
    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(20)
        
        # Title
        self.title = QLabel("Trade Simulation Metrics")
        self.title.setObjectName("PanelTitle")
        self.title.setStyleSheet("""
            QLabel#PanelTitle {
                font-size: 18px;
                font-weight: 600;
                color: #333333;
            }
        """)
        self.layout.addWidget(self.title)
        
        # Metrics grid
        self._create_metrics_grid()
        
        # Spacer
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(self.layout)
    
    def _create_metrics_grid(self):
        """Create a responsive grid of metric cards"""
        self.metrics_grid = QGridLayout()
        self.metrics_grid.setSpacing(15)
        self.metrics_grid.setContentsMargins(0, 0, 0, 0)
        
        # Metric cards configuration: (key, title, description)
        self.metrics_config = [
            ('slippage', 'Slippage', 'Price movement during trade'),
            ('fees', 'Fees', 'Exchange and network fees'),
            ('market_impact', 'Market Impact', 'Effect on market price'),
            ('net_cost', 'Net Cost', 'Total execution cost'),
            ('maker_taker', 'Maker/Taker', 'Ratio of maker to taker volume'),
            ('latency', 'Latency', 'Order processing time')
        ]
        
        self.metric_cards = {}
        
        # Create cards in a 2x3 grid
        for i, (key, title, desc) in enumerate(self.metrics_config):
            row = i // 2
            col = i % 2
            card = MetricCard(title)
            card.update_value("--", description=desc)
            self.metrics_grid.addWidget(card, row, col)
            self.metric_cards[key] = card
        
        self.layout.addLayout(self.metrics_grid)
    
    def update_metrics(self, metrics: Union[object, Dict]):
        """Update all metrics from either a SimulationMetrics object or dict"""
        if not metrics:
            self._reset_metrics()
            return
        
        # Handle both object and dictionary input
        metric_data = {}
        if hasattr(metrics, '__dict__'):  # Object case
            metric_data = {
                'slippage': getattr(metrics, 'slippage', 0),
                'fees': getattr(metrics, 'fees', 0),
                'market_impact': getattr(metrics, 'market_impact', 
                                      getattr(metrics, 'total_impact', 0)),
                'net_cost': getattr(metrics, 'net_cost', 0),
                'maker_taker': getattr(metrics, 'maker_taker_ratio', 
                                     getattr(metrics, 'maker_taker', 0)),
                'latency': getattr(metrics, 'latency_ms', 
                                 getattr(metrics, 'latency', 0))
            }
        elif isinstance(metrics, dict):  # Dictionary case
            metric_data = {
                'slippage': metrics.get('slippage', 0),
                'fees': metrics.get('fees', 0),
                'market_impact': metrics.get('market_impact', 
                                          metrics.get('total_impact', 0)),
                'net_cost': metrics.get('net_cost', 0),
                'maker_taker': metrics.get('maker_taker_ratio', 
                                        metrics.get('maker_taker', 0)),
                'latency': metrics.get('latency_ms', 
                                    metrics.get('latency', 0))
            }
        
        # Update each card with proper formatting
        self.metric_cards['slippage'].update_value(
            f"{metric_data['slippage']:.4f}%",
            metric_data['slippage'] <= 0  # Lower slippage is better
        )
        
        self.metric_cards['fees'].update_value(
            f"${metric_data['fees']:.4f}",
            metric_data['fees'] <= 0.1  # Lower fees are better
        )
        
        self.metric_cards['market_impact'].update_value(
            f"{metric_data['market_impact']:.4f}%",
            metric_data['market_impact'] <= 0  # Lower impact is better
        )
        
        self.metric_cards['net_cost'].update_value(
            f"${metric_data['net_cost']:.4f}",
            metric_data['net_cost'] <= 0  # Lower cost is better
        )
        
        self.metric_cards['maker_taker'].update_value(
            f"{metric_data['maker_taker']:.2f}",
            metric_data['maker_taker'] >= 1  # Higher ratio is better (more maker volume)
        )
        
        self.metric_cards['latency'].update_value(
            f"{metric_data['latency']:.2f}ms",
            metric_data['latency'] <= 50  # Lower latency is better
        )
    
    def _reset_metrics(self):
        """Reset all metrics to default state"""
        for card in self.metric_cards.values():
            card.update_value("--")