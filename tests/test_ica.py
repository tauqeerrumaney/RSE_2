import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import sys
import os

sys.path.append(os.path.join("workflow", "scripts"))
import ica

@patch('ica.configure_logger')
@patch('ica.get_path')
@patch('ica.pd.read_feather')
@patch('ica.mne.create_info')
@patch('ica.mne.channels.make_standard_montage')
@patch('ica.mne.EpochsArray')
@patch('ica.ICA')
@patch('ica.plt')
def test_main_valid_data(self, mock_plt, mock_ica, mock_epochs_array, 
                         mock_make_montage, mock_create_info, mock_read_feather, 
                         mock_get_path, mock_configure_logger):
    # Mock the logger
    mock_logger = MagicMock()
    mock_configure_logger.return_value = mock_logger
    
    # Mock get_path to return different paths for input and output
    mock_get_path.side_effect = lambda x: x
    
    # Mock the DataFrame returned by pd.read_feather
    mock_df = pd.DataFrame({
        'event': [1, 1, 2, 2],
        'channel': ['Fp1', 'Fp2', 'F7', 'F8'],
        'signal': [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]],
        'size': [2, 2, 2, 2],
        'code': [100, 100, 200, 200]
    })
    mock_read_feather.return_value = mock_df

    # Create mocks for other dependencies
    mock_info = MagicMock()
    mock_create_info.return_value = mock_info
    mock_montage = MagicMock()
    mock_make_montage.return_value = mock_montage
    mock_epochs = MagicMock()
    mock_epochs.copy.return_value = mock_epochs
    mock_epochs_array.return_value = mock_epochs
    mock_ica_instance = MagicMock()
    mock_ica.return_value = mock_ica_instance

    # Mock the open function to return file-like objects for different files
    mock_files = {
        'artifacts.txt': "1,2,3\n",
        'input.feather': "",
        'output.fif': "",
        'plot.png': ""
    }
    
    def mock_open_wrapper(file, mode='r'):
        return mock_open(read_data=mock_files.get(file, ""))(file, mode)

    with patch('builtins.open', mock_open_wrapper):
        # Call the main function with the correct arguments
        ica.main('input.feather', 'output.fif', 'plot.png', 'artifacts.txt', False)

    # Assert log calls for debugging
    expected_log_calls = [
        'Reading data from input.feather',
        'Finished reading data. Applying ICA',
        'Processing data for 2 events',
        'Shape of epochs_data:',
        'ICA component plots saved to plot.png',
        'Loaded additional artifacts: [1, 2, 3]',
        'Cleaned data saved to output.fif'
    ]
    actual_log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
    for message in expected_log_calls:
        self.assertTrue(any(message in call for call in actual_log_calls), 
                        f"Expected log message '{message}' not found")

    # Check for no error logs
    self.assertFalse(mock_logger.error.called, "An error was logged unexpectedly")

    # Verify key function calls
    mock_ica.assert_called_once()
    mock_ica_instance.fit.assert_called_once_with(mock_epochs)

if __name__ == '__main__':
    unittest.main()
