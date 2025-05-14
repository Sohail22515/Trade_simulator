from pathlib import Path
from PyQt5.QtCore import QFile, QTextStream
from trade_simulator.utils.logging import get_logger

logger = get_logger(__name__)

def load_stylesheet(style_name: str = "default") -> str:
    """Load and return a Qt stylesheet from the resources/styles directory"""
    try:
        # Get the absolute path to the stylesheet
        current_dir = Path(__file__).parent
        stylesheet_path = current_dir / "styles" / f"{style_name}.qss"
        
        if not stylesheet_path.exists():
            logger.warning(f"Stylesheet not found at: {stylesheet_path}")
            return DEFAULT_STYLE
            
        # Read the stylesheet file
        file = QFile(str(stylesheet_path))
        if not file.open(QFile.ReadOnly | QFile.Text):
            logger.warning(f"Could not open stylesheet: {stylesheet_path}")
            return DEFAULT_STYLE
            
        stream = QTextStream(file)
        return stream.readAll()
        
    except Exception as e:
        logger.error(f"Error loading stylesheet: {e}")
        return DEFAULT_STYLE

# Fallback default styles if file is missing
DEFAULT_STYLE = """
QMainWindow {
    background-color: #f0f0f0;
    font-family: 'Segoe UI';
}
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 8px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #45a049;
}
"""