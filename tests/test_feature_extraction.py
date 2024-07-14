"""
Module: test_feature_extraction
Description: This module contains unit tests for the functions
             in the feature_extraction module.
"""

import os
import unittest
from unittest.mock import patch

import mne
import numpy as np

from path_utils import extend_sys_path

with extend_sys_path(os.path.join("workflow", "scripts")):
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
            'ch1_mean': np.array([-0.04525671]),
            'ch1_std': np.array([0.98703316]),
            'ch1_max': np.array([2.75935511]),
            'ch1_min': np.array([-3.04614305]),
            'ch1_kurtosis': np.array([-0.04676632]),
            'ch1_skewness': np.array([0.03385895]),
            'ch1_wavelet_0_mean': np.array([0.68780501]),
            'ch1_wavelet_0_std': np.array([2.89026408]),
            'ch1_wavelet_1_mean': np.array([-0.15368656]),
            'ch1_wavelet_1_std': np.array([0.83737634]),
            'ch1_wavelet_2_mean': np.array([0.08943787]),
            'ch1_wavelet_2_std': np.array([0.89597881]),
            'ch1_wavelet_3_mean': np.array([-0.03778026]),
            'ch1_wavelet_3_std': np.array([0.972202]),
            'ch1_wavelet_4_mean': np.array([0.07335742]),
            'ch1_wavelet_4_std': np.array([0.90946569]),
            'ch1_wavelet_5_mean': np.array([-0.02770826]),
            'ch1_wavelet_5_std': np.array([1.00921858]),
            'ch1_delta_power': np.array([0., 0.]),
            'ch1_theta_power': np.array([0., 0.]),
            'ch1_alpha_power': np.array([0., 0.]),
            'ch1_beta_power': np.array([0., 0.]),
            'ch1_gamma_power': np.array([0., 0.]),
            'ch1_sample_entropy': np.array([2.24417546]),
            'ch1_approx_entropy': np.array([1.6889074]),
        }

        channel = "ch1"
        for key_suffix, expected_value in expected_features.items():
            feature_key = f"{key_suffix}"
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
