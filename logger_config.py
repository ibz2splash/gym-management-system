
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
 
# Import Python's built-in logging library — handles all the log-writing for us.
import logging
# Import the os module so we can check for and create the logs/ folder.
import os
 
 
# Define the function that builds and returns a configured Logger object.
# Default name is "gym_app" so every file imports the same logger.
def setup_logger(name: str = "gym_app") -> logging.Logger:
    """
    Configure and return a logger instance.
 
    The logger writes to both a file and the console.
    File handler captures everything from INFO upward.
    Console handler shows WARNING and above to avoid clutter.
    """
    # Ensure logs directory exists
    # Set the folder name where log files will live.
    log_dir = "logs"
    # If the logs/ folder doesn't already exist on disk...
    if not os.path.exists(log_dir):
        # ...create it. Prevents a crash on the very first run.
        os.makedirs(log_dir)
 
    # Build the full path to the log file: logs/gym_app.log
    log_file = os.path.join(log_dir, "gym_app.log")
 
    # Get (or create) a logger with the given name. Same name = same logger.
    logger = logging.getLogger(name)
    # Set the minimum level this logger will process — INFO and above.
    logger.setLevel(logging.INFO)
 
    # Avoid adding duplicate handlers if setup_logger is called multiple times
    # If handlers are already attached (e.g. from a re-import), return early
    # so we don't double-attach and end up writing every log entry twice.
    if logger.handlers:
        return logger
 
    # Formatter — timestamp, level, module, message
    # Define what every log line will look like: time | level | name | message.
    # The -8 pads the level name to 8 characters so columns line up visually.
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
 
    # File handler (INFO and above)
    # Create a handler that writes log lines to the file (UTF-8 for safety).
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    # File handler captures everything from INFO upward — full audit trail.
    file_handler.setLevel(logging.INFO)
    # Apply the formatter so file lines have timestamps and structure.
    file_handler.setFormatter(formatter)
    # Attach the file handler to the logger.
    logger.addHandler(file_handler)
 
    # Console handler (WARNING and above so the user isn't flooded)
    # Create a handler that prints log lines to the terminal.
    console_handler = logging.StreamHandler()
    # Only show WARNING and above on screen — avoids spamming the user.
    console_handler.setLevel(logging.WARNING)
    # Same formatter so console lines match the file format.
    console_handler.setFormatter(formatter)
    # Attach the console handler to the logger.
    logger.addHandler(console_handler)
 
    # Hand the fully configured logger back to whoever called this function.
    return logger
 
 
# Create a default logger that other modules can import
# Build the global logger object now, so every other file can do
# `from logger_config import log` and immediately have a working logger.
log = setup_logger()