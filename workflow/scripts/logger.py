"""
This module configures and returns a logger.

The module provides a function to configure a logger with a specified name.
The logger outputs debug-level and higher messages to the console.

Functions:
    configure_logger(name):
        Configures and returns a logger with the specified name.
"""

import logging
import sys


def configure_logger(name: str):
    """
    Configure a logger with the given name.

    This function sets up a logger with a specified name, configures it to log
    debug-level messages to the console, and formats the log messages.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create console handler and set level to debug
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)

    return logger
