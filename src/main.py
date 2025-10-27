"""
Smart Focus Timer - Main Entry Point
AI-Powered Productivity Timer with Face Detection
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import logging

from utils.logger import setup_logging
from utils.config import get_config
from ui.main_window import MainWindow

# Enable high DPI scaling
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging(log_level="INFO", log_to_file=True)
    logger = logging.getLogger(__name__)

    logger.info("="* 50)
    logger.info("Smart Focus Timer - Starting Application")
    logger.info("="* 50)

    # Load configuration
    config = get_config()
    logger.info(f"Configuration loaded: {config.config_file}")

    try:
        # Create Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName("Smart Focus Timer")
        app.setOrganizationName("FocusLab")
        app.setApplicationVersion("2.0.0")

        # Create and show main window
        window = MainWindow()
        window.show()

        logger.info("Application started successfully")

        # Run application
        sys.exit(app.exec_())

    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
