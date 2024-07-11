import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import mne
import os
import sys
sys.path.append(os.path.join("workflow", "scripts"))
from feature_extraction import extract_features, main

class TestFeatureExtraction(unittest.TestCase):
    
    def setUp(self):
        # Create mock EEG data
        self.sfreq = 100
        self.n_channels = 5
        self.n_times = 1000
        self.n_epochs = 10
        
        self.data = np.random.randn(self.n_epochs, self.n_channels, self.n_times)
        self.info = mne.create_info(ch_names=['ch1', 'ch2', 'ch3', 'ch4', 'ch5'], sfreq=self.sfreq)
        self.mock_epochs = mne.EpochsArray(self.data, self.info)

    @patch('feature_extraction.welch')
    def test_extract_features(self, mock_welch):
        # Mock the output of the welch function
        mock_freqs = np.linspace(0, 50, 100)
        mock_psd = np.random.randn(self.n_epochs, len(mock_freqs))
        mock_welch.return_value = (mock_freqs, mock_psd)
        
        feature_types = ["statistical", "wavelet", "psd", "entropy"]
        features = extract_features(self.mock_epochs, feature_types)
        
        # Check if features are extracted for all channels
        for channel in ['ch1', 'ch2', 'ch3', 'ch4', 'ch5']:
            self.assertIn(f"{channel}_mean", features)
            self.assertIn(f"{channel}_std", features)
            self.assertIn(f"{channel}_max", features)
            self.assertIn(f"{channel}_min", features)
            self.assertIn(f"{channel}_kurtosis", features)
            self.assertIn(f"{channel}_skewness", features)
            for band in ["delta", "theta", "alpha", "beta", "gamma"]:
                self.assertIn(f"{channel}_{band}_power", features)
            self.assertIn(f"{channel}_sample_entropy", features)
            self.assertIn(f"{channel}_approx_entropy", features)

    @patch('feature_extraction.mne.read_epochs')
    @patch('feature_extraction.welch')
    @patch('feature_extraction.get_path')
    @patch('feature_extraction.np.save')
    @patch('feature_extraction.os.path.exists')
    @patch('feature_extraction.configure_logger')
    def test_main(self, mock_configure_logger, mock_exists, mock_save, mock_get_path, mock_welch, mock_read_epochs):
        # Mock logger
        mock_logger_instance = MagicMock()
        mock_configure_logger.return_value = mock_logger_instance

        # Mock read_epochs to return the mock_epochs
        mock_read_epochs.return_value = self.mock_epochs
        
        # Mock the get_path function to just return the filename
        mock_get_path.side_effect = lambda x: x
        
        # Mock the welch function
        mock_freqs = np.linspace(0, 50, 100)
        mock_psd = np.random.randn(self.n_epochs, len(mock_freqs))
        mock_welch.return_value = (mock_freqs, mock_psd)
        
        # Mock os.path.exists to return True
        mock_exists.side_effect = lambda x: True
        
        # Set up arguments
        infile = 'test_infile.fif'
        outfile = 'test_outfile.npy'
        features = ["statistical", "wavelet", "psd", "entropy"]
        
        # Run the main function
        main(infile, outfile, features)
        
        # Check if np.save was called
        mock_save.assert_called_once()
        saved_features = mock_save.call_args[0][1]
        
        # Check if features are extracted for all channels
        for channel in ['ch1', 'ch2', 'ch3', 'ch4', 'ch5']:
            self.assertIn(f"{channel}_mean", saved_features)
            self.assertIn(f"{channel}_std", saved_features)
            self.assertIn(f"{channel}_max", saved_features)
            self.assertIn(f"{channel}_min", saved_features)
            self.assertIn(f"{channel}_kurtosis", saved_features)
            self.assertIn(f"{channel}_skewness", saved_features)
            for band in ["delta", "theta", "alpha", "beta", "gamma"]:
                self.assertIn(f"{channel}_{band}_power", saved_features)
            self.assertIn(f"{channel}_sample_entropy", saved_features)
            self.assertIn(f"{channel}_approx_entropy", saved_features)

if __name__ == '__main__':
    unittest.main()
