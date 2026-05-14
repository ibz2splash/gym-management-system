"""
logger_config.py
----------------
Central logging configuration for the Gym Management System.
Implements:
    - INFO level for normal application flow
    - ERROR level for failures
    - Logs written to file (logs/gym_app.log) and console

Covers Part G of the assignment.
"""

import logging
import os


def setup_logger(name: str = "gym_app") -> logging.Logger:
    """
    Configure and return a logger instance.

    The logger writes to both a file and the console.
    File handler captures everything from INFO upward.
    Console handler shows WARNING and above to avoid clutter.
    """
    # Ensure logs directory exists
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "gym_app.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    # Formatter — timestamp, level, module, message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler (INFO and above)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (WARNING and above so the user isn't flooded)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Create a default logger that other modules can import
log = setup_logger()
