import unittest
import logging
from io import StringIO
import sys
import os

sys.path.append(os.path.join("workflow", "scripts"))
from logger import configure_logger

class TestLogger(unittest.TestCase):
    """
    Test suite for the logging configuration function in the `logger` module.
    """

    def setUp(self):
        """
        Set up the test environment before each test.

        This includes resetting the root logger and capturing the log output.
        """
        # Clear all existing handlers from the root logger
        logging.root.handlers.clear()

        # Capture the log output
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

    def tearDown(self):
        """
        Clean up the test environment after each test.

        This includes clearing the log capture.
        """
        self.log_capture.truncate(0)
        self.log_capture.seek(0)

    def test_configure_logger(self):
        """
        Test that the logger is created with the correct name.
        """
        logger = configure_logger(name='test_logger')
        self.assertEqual(logger.name, "test_logger")

    def test_logger_level(self):
        """
        Test that the logger's effective level is INFO.
        """
        logger = configure_logger(name='test_logger')

        # Validate the effective level by logging an INFO message and checking the output
        logger.addHandler(self.handler)
        logger.info("Checking logger level")
        log_output = self.log_capture.getvalue()

        # Assert that the INFO message appears in the log output
        self.assertIn("INFO - Checking logger level", log_output)

        # Assert that DEBUG message does not appear in the log output
        self.assertNotIn("DEBUG", log_output)

    def test_log_format(self):
        """
        Test that the log format is correct.

        Verifies that the log message contains the expected components.
        """
        logger = configure_logger(name='test_logger')
        logger.addHandler(self.handler)
        logger.info("Test message")
        log_output = self.log_capture.getvalue()
        
        # Check if the log output contains all required elements
        self.assertIn("test_logger", log_output)
        self.assertIn("INFO", log_output)
        self.assertIn("Test message", log_output)

    def test_different_log_levels(self):
        """
        Test different log levels.

        Verifies that the logger outputs messages for levels INFO and above, and not for DEBUG.
        """
        logger = configure_logger(name='test_logger')
        logger.addHandler(self.handler)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        log_output = self.log_capture.getvalue()
        
        # Check that debug message is not in the output
        self.assertNotIn("Debug message", log_output)
        self.assertIn("Info message", log_output)
        self.assertIn("Warning message", log_output)
        self.assertIn("Error message", log_output)
        self.assertIn("Critical message", log_output)

if __name__ == '__main__':
    unittest.main()
