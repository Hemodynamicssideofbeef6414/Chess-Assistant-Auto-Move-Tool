import os
import logging
from PyQt6.QtGui import QIcon, QPixmap
from utils.resource_path import resource_path

logger = logging.getLogger(__name__)

def set_window_icon(app):
    # Try multiple logo locations and formats
    logo_candidates = [
        resource_path(os.path.join('assets', 'logo.png')),
        resource_path(os.path.join('assets', 'Logo.png')),
        resource_path(os.path.join('assets', 'logo.jpg')),
        resource_path(os.path.join('assets', 'Logo.jpg')),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'assets', 'Logo.jpg'),
    ]
    
    for logo_path in logo_candidates:
        if os.path.exists(logo_path):
            try:
                icon = QIcon(logo_path)
                if not icon.isNull():
                    app.setWindowIcon(icon)
                    logger.debug(f"Window icon set from: {logo_path}")
                    return
            except Exception as e:
                logger.warning(f"Failed to set window icon from {logo_path}: {e}")
    
    logger.warning("No logo file found for window icon")
