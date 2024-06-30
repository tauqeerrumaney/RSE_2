"""
This module provides utility functions for file handling.

It includes functions for configuring logging, getting file paths, and more.
"""

import os

def get_path(file_name, folder="data"):
    """
    Returns the file path for a given file name and folder.

    Parameters:
    file_name (str): The name of the file.
    folder (str, optional): The name of the folder where the file is located.
        Defaults to "data".

    Returns:
    str: The file path.

    """
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, f"../{folder}/{file_name}")
    return file_path
