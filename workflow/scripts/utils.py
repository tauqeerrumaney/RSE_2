import os


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
