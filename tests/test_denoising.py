"""
Module: test_denoising
Description: This module contains unit tests for the denoising functionality
in the `denoising` module.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

import mne
import numpy as np

from path_utils import extend_sys_path

with extend_sys_path(os.path.join("workflow", "scripts")):
    import denoising


class TestDenoising(unittest.TestCase):
    """
    Test suite for the denoising functions in the `denoising` module.
    """
    @patch('denoising.configure_logger')
    @patch('denoising.get_path')
    @patch('os.path.exists')
    @patch('mne.read_epochs')
    def test_main_valid_data(
            self,
            mock_read_epochs,
            mock_exists,
            mock_get_path,
            mock_configure_logger):
        """
        Test the main function with valid data.

        Mocks external dependencies and verifies the behavior and log outputs.
        """
        mock_logger = MagicMock()
        mock_configure_logger.return_value = mock_logger

        # Mock get_path to return the file paths directly
        mock_get_path.side_effect = lambda x: x

        # Mock os.path.exists to return True for any path check
        mock_exists.return_value = True

        # Create a mock MNE Epochs object with sample data
        data = np.random.randn(10, 1000)  # 10 channels, 1000 samples
        info = mne.create_info(
            ch_names=[
                str(i) for i in range(10)],
            sfreq=100,
            ch_types='eeg')
        mock_epochs = mne.EpochsArray(data[np.newaxis, :], info)

        # Mock the read_epochs method to return the mock_epochs
        mock_read_epochs.return_value = mock_epochs

        # Mock the save method
        with patch.object(mock_epochs, 'save', return_value=None) as mock_save:
            # Call the main function with the correct arguments
            denoising.main('input.fif', 'output.fif')

            # Check that the data was read correctly
            mock_read_epochs.assert_called_once_with('input.fif', preload=True)

            # Check that the re-referencing was applied correctly
            self.assertTrue(mock_epochs.info['projs'])

            # Check that the cleaned data was saved correctly
            mock_save.assert_called_once_with('output.fif', overwrite=True)

    @patch('denoising.get_path')
    @patch('os.path.exists')
    def test_input_file_not_found(self, mock_exists, mock_get_path):
        """Test handling of FileNotFoundError when input file is missing."""
        # Mock get_path to return the file path directly
        mock_get_path.side_effect = lambda x: x
        mock_exists.side_effect = lambda x: x != 'input.fif'

        with self.assertRaises(FileNotFoundError):
            denoising.main('input.fif', 'output.fif')

    @patch('denoising.get_path')
    @patch('os.path.exists')
    def test_invalid_input_type(self, mock_exists, mock_get_path):
        """Test handling of TypeError when input types are incorrect."""
        # Mock get_path to return the file path directly
        mock_get_path.side_effect = lambda x: x
        mock_exists.return_value = True

        with self.assertRaises(TypeError):
            denoising.main(123, 'output.fif')  # Invalid infile type

        with self.assertRaises(TypeError):
            denoising.main('input.fif', 456)  # Invalid outfile type


if __name__ == '__main__':
    unittest.main()
