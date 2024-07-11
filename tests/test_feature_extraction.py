"""
Module: test_feature_extraction
Description: This module contains unit tests for the functions
             in the feature_extraction module.
"""

import unittest
from unittest.mock import patch
import numpy as np
import mne
import os
import sys
sys.path.append(os.path.join("workflow", "scripts"))
from feature_extraction import extract_features

class TestFeatureExtraction(unittest.TestCase):
    """
    Test suite for the feature_extraction module.
    """

    def setUp(self):
        """
        Set up the test environment by creating mock EEG data.
        """
        np.random.seed(0)
        self.sfreq = 100
        self.n_channels = 5
        self.n_times = 1000
        self.n_epochs = 1

        # Create mock EEG data
        self.data = np.random.randn(
            self.n_epochs, self.n_channels, self.n_times)
        self.info = mne.create_info(
            ch_names=['ch1', 'ch2', 'ch3', 'ch4', 'ch5'],
            sfreq=self.sfreq
        )
        self.mock_epochs = mne.EpochsArray(self.data, self.info)

    @patch('feature_extraction.welch', autospec=True)
    def test_extract_features(self, mock_welch):
        """
        Test extract_features function with mocked welch function.

        Verifies that the extracted features match the expected values.
        """
        # Mock the output of the welch function
        mock_freqs = np.linspace(0, 50, 2)
        psd = np.array([[-0.8, -0.4], [0.3, -0.01]])
        mock_welch.return_value = (mock_freqs, psd)

        # Define feature types to extract
        feature_types = ["statistical", "wavelet", "psd", "entropy"]
        features = extract_features(self.mock_epochs, feature_types)

        # Expected feature values for channel 'ch1'
        expected_features = {
            'ch1_mean': [-0.04525671],
            'ch1_std': [0.97267244],
            'ch1_max': [3.56706532],
            'ch1_min': [-2.99939714],
            'ch1_kurtosis': [-0.15153331],
            'ch1_skewness': [-0.000301],
            'ch1_wavelet_0_mean': [0.2251093],
            'ch1_wavelet_0_std': [1.12064203],
            'ch1_wavelet_1_mean': [0.02524351],
            'ch1_wavelet_1_std': [0.92669826],
            'ch1_wavelet_2_mean': [-0.11906461],
            'ch1_wavelet_2_std': [1.03268539],
            'ch1_wavelet_3_mean': [0.02321793],
            'ch1_wavelet_3_std': [1.00711005],
            'ch1_wavelet_4_mean': [0.15906194],
            'ch1_wavelet_4_std': [1.01269121],
            'ch1_wavelet_5_mean': [-0.06254589],
            'ch1_wavelet_5_std': [1.00652331],
            'ch1_delta_power': [0., 0.],
            'ch1_theta_power': [0., 0.],
            'ch1_alpha_power': [0., 0.],
            'ch1_beta_power': [0., 0.],
            'ch1_gamma_power': [0., 0.],
            'ch1_sample_entropy': [2.24808718],
            'ch1_approx_entropy': [1.68016063],
        }

        channel = "ch1"
        for key_suffix, expected_value in expected_features.items():
            feature_key = f"{channel}_{key_suffix.split('_')[1]}"
            with self.subTest(channel=channel, feature=feature_key):
                self.assertIn(
                    feature_key,
                    features,
                    f"{feature_key} not found in extracted features"
                )
                np.testing.assert_array_almost_equal(
                    features[feature_key], expected_value
                )


if __name__ == '__main__':
    unittest.main()
