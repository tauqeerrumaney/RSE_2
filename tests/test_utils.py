"""
Module: test_utils
Description: This module contains unit tests for the get_path functions
in the util module.
"""
import os
import unittest
from unittest.mock import patch

from path_utils import extend_sys_path

with extend_sys_path(os.path.join("workflow", "scripts")):
    from utils import get_path


class TestGetPath(unittest.TestCase):
    """Unit tests for the 'get_path' function in the 'utils' module."""

    def test_absolute_path(self):
        """Test that an absolute path is returned unchanged."""
        abs_path = "/home/user/documents/file.txt"
        self.assertEqual(get_path(abs_path), abs_path)

    def test_relative_path(self):
        """Test that a relative path is converted to an absolute path."""
        rel_path = "documents/file.txt"
        expected_path = os.path.abspath(rel_path)
        self.assertEqual(get_path(rel_path), expected_path)

    def test_user_home_expansion(self):
        """Test that paths with '~' are expanded correctly."""
        home_path = "~/documents/file.txt"
        expected_path = os.path.abspath(os.path.expanduser(home_path))
        self.assertEqual(get_path(home_path), expected_path)

    @patch('os.path.expanduser')
    @patch('os.path.abspath')
    def test_function_calls(self, mock_abspath, mock_expanduser):
        """Test that the function calls expanduser and abspath."""
        mock_expanduser.return_value = "/expanded/path"
        mock_abspath.return_value = "/absolute/expanded/path"

        result = get_path("~/some/path")

        mock_expanduser.assert_called_once_with("~/some/path")
        mock_abspath.assert_called_once_with("/expanded/path")
        self.assertEqual(result, "/absolute/expanded/path")

    def test_empty_string(self):
        """Test behavior with an empty string input."""
        self.assertEqual(get_path(""), os.path.abspath(""))

    def test_current_directory(self):
        """Test behavior with current directory '.'"""
        self.assertEqual(get_path("."), os.path.abspath("."))

    def test_parent_directory(self):
        """Test behavior with parent directory '..'"""
        self.assertEqual(get_path(".."), os.path.abspath(".."))


if __name__ == '__main__':
    unittest.main()
