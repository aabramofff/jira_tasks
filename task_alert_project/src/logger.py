import logging
import os
from logging.handlers import RotatingFileHandler


os.makedirs("logs", exist_ok=True)


def setup_logger(name, log_file, level=logging.INFO):
    """
    Configures and returns a logger instance with log rotation capabilities.

    Args:
        name (str): Unique name for the logger
        log_file (str): Path to the output log file.
        level (int): Logging level (e.g., INFO, ERROR)

    Returns:
        logging.Logger: A configured legger object.
    """
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


alert_logger = setup_logger("alert_logger", "logs/alerts.log")
