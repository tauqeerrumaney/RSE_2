import os


def get_path(filepath: str) -> str:
    """Get the absolute path of a file.

    Args:
        filepath (str): The file path.

    Returns:
        str: The absolute path of the file.
    """
    # Expand user (~) and resolve relative paths
    user_defined_path = os.path.expanduser(filepath)
    absolute_path = os.path.abspath(user_defined_path)
    return absolute_path
