import os

from workflow.scripts.logger import configure_logger

from utils import get_path


def get_path(filepath):
    """
    Returns the absolute file path for a given relative file.

    Parameters:
    filepath (str): The relative file path.

    Returns:
    str: The file path.
    """
    # Expand user (~) and resolve relative paths
    user_defined_path = os.path.expanduser(filepath)
    absolute_path = os.path.abspath(user_defined_path)
    return absolute_path


def get_text(keyword):
    """
    Retrieves the text content associated with the given keyword.

    Args:
        keyword (str): The keyword used to identify the text content.

    Returns:
        str: The text content associated with the keyword,
            or None if the file is not found.

    Raises:
        FileNotFoundError: If the keyword file is not found.
        Exception: If an unexpected error occurs while reading the file.
    """
    # Configure logger
    logger = configure_logger()

    try:
        with open(get_path(f"data/textblocks/{keyword}.txt"), "r") as file:
            keyword_text = file.read()
        return keyword_text
    except FileNotFoundError as fnfe:
        logger.error(f"FileNotFoundError: {fnfe}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    return False
