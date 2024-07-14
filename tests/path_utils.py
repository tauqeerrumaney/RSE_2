"""
Utilities for working with paths in tests.
"""
import sys
from contextlib import contextmanager


@contextmanager
def extend_sys_path(path):
    """
    Extend the sys.path with the given path for the duration of the context.

    Args:
        path (str): The path to add to sys.path.

    Usage:
        ```python
        with extend_sys_path("path/to/module"):
            import module
        ```
    """
    original_sys_path = sys.path[:]
    sys.path.append(path)
    try:
        yield
    finally:
        sys.path = original_sys_path
