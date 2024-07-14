"""
This script loads denoised EEG data from a file, extracts various
 features(statistical, wavelet, PSD, and entropy) from the data,
 and saves the extracted features to a new file.

Usage:
    Run the script from the command line with the following options:

    ```
    python feature_extraction.py infile outfile [--features FEATURE_TYPES]
    ```

    Example:
    ```
    python feature_extraction.py denoised_epo.fif features.npy
    ```

Options:
    infile (str): Path to the input file containing the denoised EEG data.
    outfile (str): Path to the file where extracted features are saved.
    --features (list, optional): List of feature types to extract.
                       Default: ["statistical", "wavelet", "psd", "entropy"]

Files:
    infile: The input file containing the denoised EEG data in the FIF format.
    outfile: The output file where the extracted features will be saved in the
              npy format.

Functions:
    extract_features(epochs, feature_types):
        Extracts specified features from the EEG epochs.
    main(infile, outfile, features):
        Main function to load, extract, and save EEG signal features.
"""

import argparse
import os
import traceback

import mne
import numpy as np
import pywt
from antropy import entropy as ent
from scipy.signal import welch
from scipy.stats import kurtosis, skew

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def extract_features(epochs, feature_types):
    """
    Extracts various features from EEG data.

    This function computes statistical, wavelet, power spectral density (PSD),
    and entropy features for each channel in the EEG data provided.
    The features are computed based on the specified types in `feature_types`.

    Args:
        epochs (mne.Epochs): An MNE Epochs object containing the EEG data.
        feature_types (list): A list of strings specifying which types of
            features to compute. Possible values include
            "statistical", "wavelet", "psd", and "entropy".

    Returns:
        A dictionary where keys are feature names composed of the channel name
        followed by an underscore and the feature name (and for wavelet
        features, an additional underscore and index). Each value is a NumPy
        array containing the computed feature(s) for that channel.
        Example structure:
        {
            "ch1_mean": np.array([...]),
            "ch1_std": np.array([...]),
            ...
            "ch1_wavelet_0_mean": np.array([...]),
            ...
            "ch1_delta_power": np.array([...]),
            ...
            "ch1_sample_entropy": np.array([...]),
            ...
            "ch2_mean": np.array([...]),
            ...
        }

    Raises:
        ValueError: If an invalid feature type is specified.
    """
    features = {}
    data = epochs.get_data(copy=False)
    channel_names = epochs.info["ch_names"]
    sfreq = epochs.info["sfreq"]

    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
        "gamma": (30, 45),
    }

    logger.info("Extracting features for %d channels", len(channel_names))
    for i, channel in enumerate(channel_names):
        channel_data = data[:, i, :]

        if "statistical" in feature_types:
            mean = np.mean(channel_data, axis=1)
            std = np.std(channel_data, axis=1)
            max_val = np.max(channel_data, axis=1)
            min_val = np.min(channel_data, axis=1)
            kurt = kurtosis(channel_data, axis=1)
            skewness = skew(channel_data, axis=1)

            features[f"{channel}_mean"] = mean
            features[f"{channel}_std"] = std
            features[f"{channel}_max"] = max_val
            features[f"{channel}_min"] = min_val
            features[f"{channel}_kurtosis"] = kurt
            features[f"{channel}_skewness"] = skewness

        if "wavelet" in feature_types:
            coeffs = pywt.wavedec(channel_data, "db4", level=5, axis=1)
            for j, coeff in enumerate(coeffs):
                features[f"{channel}_wavelet_{j}_mean"] = np.mean(
                    coeff, axis=1
                )
                features[f"{channel}_wavelet_{j}_std"] = np.std(coeff, axis=1)

        if "psd" in feature_types:
            freqs, psd = welch(channel_data, sfreq, nperseg=248)
            for band, (low, high) in bands.items():
                band_power = np.sum(
                    psd[:, (freqs >= low) & (freqs <= high)], axis=1
                )
                features[f"{channel}_{band}_power"] = band_power

        if "entropy" in feature_types:
            samp_entropy = np.array(
                [ent.sample_entropy(ch) for ch in channel_data]
            )
            app_entropy = np.array(
                [ent.app_entropy(ch) for ch in channel_data]
            )
            features[f"{channel}_sample_entropy"] = samp_entropy
            features[f"{channel}_approx_entropy"] = app_entropy

    return features


def main(infile: str, outfile: str, features: list[str]):
    """
    Main function to load, extract, and save EEG signal features.

    This function loads denoised EEG data from the specified input file,
    extracts various features from the data, and saves the extracted
    features to the specified output file.

    Args:
        infile (str): Path to the file containing the denoised EEG data.
        outfile (str): Path to the file where extracted features are saved.
        features (list, optional): A list of strings specifying which types
          of features to extract. Possible values include "statistical",
          "wavelet", "psd", and "entropy".

    Returns:
        None

    Raises:
        FileNotFoundError: If the input file does not exist.
        TypeError: If the input parameters are not of the expected types.
        ValueError: If the output directory does not exist.
    """
    # Validate input types
    if not isinstance(infile, str):
        raise TypeError(
            f"Expected 'infile' to be of type str, but got "
            f"{type(infile).__name__}"
        )
    if not isinstance(outfile, str):
        raise TypeError(
            f"Expected 'outfile' to be of type str, but got "
            f"{type(outfile).__name__}"
        )
    if not isinstance(features, list):
        raise TypeError(
            f"Expected 'features' to be of type list, but got "
            f"{type(features).__name__}"
        )
    if not all(isinstance(feature, str) for feature in features):
        raise TypeError(
            "Expected all elements in 'features' to be of type str"
        )

    # Validate input file
    in_path = get_path(infile)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    # Validate output file
    out_path = get_path(outfile)
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        raise ValueError(f"Output directory does not exist: {out_dir}")

    # Read the data from the input file
    logger.info("Reading data from %s", in_path)
    epochs = mne.read_epochs(in_path, preload=True)
    logger.info("Finished reading data. Extracting features")

    features = extract_features(epochs, features)

    np.save(out_path, features)
    logger.info("Extracted features saved to %s", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile",
        type=str,
        help="name of the file to load",
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="name of the file to save extracted features",
    )
    parser.add_argument(
        "--features",
        "-f",
        nargs="+",
        choices=["statistical", "wavelet", "psd", "entropy"],
        default=["statistical", "wavelet", "psd", "entropy"],
        help="types of features to extract",
    )

    args = parser.parse_args()
    try:
        main(infile=args.infile, outfile=args.outfile, features=args.features)
    except (TypeError, ValueError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
