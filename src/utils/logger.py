"""
Logging Configuration
Sets up application-wide logging
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_to_file: bool = True, log_dir: str = "logs"):
    """
    Set up application logging

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files
    """
    # Create log directory
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        log_file = log_path / f"focus_timer_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Silence some noisy libraries
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    root_logger.info("Logging initialized")
