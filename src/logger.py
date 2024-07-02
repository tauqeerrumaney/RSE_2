"""
Module for configuring logging.

This module provides a function to configure a logger with a specified name.
The logging configuration includes  timestamp, logger name, log level, message.

Example usage:
    from logger import configure_logger

    logger = configure_logger('my_script')
    logger.info('This is an info message')
"""

import logging


def configure_logger(name):
    """
    Configures and returns a logger with the specified name.

    This sets up the logging config with specific format and log level.
    It is configured to include timestamp, logger name, log level, message

    Args:
        name (str): The name to be used for the logger.

    Returns:
        logging.Logger: Configured logger instance.

    Example:
        logger = configure_logger('my_script')
        logger.info('This is an info message')
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(name)
    return logger
