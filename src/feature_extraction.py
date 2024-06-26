import mne
import argparse
import numpy as np
import pywt
from scipy.stats import kurtosis, skew
from scipy.signal import welch
from utils import logger, set_path
from antropy import entropy as ent


# TODO let nperseg be the min of channel size
def compute_psd(data, sfreq, nperseg=248):
    freqs, psd = welch(data, sfreq, nperseg=nperseg)
    return freqs, psd


def extract_features(epochs, feature_types):
    # Initialize a dictionary to hold features
    features = {}

    # Get data array and channel names
    data = epochs.get_data()
    channel_names = epochs.info["ch_names"]
    sfreq = epochs.info["sfreq"]

    # Define frequency bands
    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
        "gamma": (30, 45),
    }

    # Loop through each channel
    for i, channel in enumerate(channel_names):
        channel_data = data[:, i, :]

        # Compute statistical features
        if "statistical" in feature_types:
            mean = np.mean(channel_data, axis=1)
            std = np.std(channel_data, axis=1)
            max_val = np.max(channel_data, axis=1)
            min_val = np.min(channel_data, axis=1)
            kurt = kurtosis(channel_data, axis=1)
            skewness = skew(channel_data, axis=1)

            # Store statistical features
            features[f"{channel}_mean"] = mean
            features[f"{channel}_std"] = std
            features[f"{channel}_max"] = max_val
            features[f"{channel}_min"] = min_val
            features[f"{channel}_kurtosis"] = kurt
            features[f"{channel}_skewness"] = skewness

        # Compute wavelet features using Discrete Wavelet Transform (DWT)
        if "wavelet" in feature_types:
            coeffs = pywt.wavedec(channel_data, "db4", level=5, axis=1)
            for j, coeff in enumerate(coeffs):
                features[f"{channel}_wavelet_{j}_mean"] = np.mean(coeff, axis=1)
                features[f"{channel}_wavelet_{j}_std"] = np.std(coeff, axis=1)

        # Compute power spectral density (PSD) and band power
        if "psd" in feature_types:
            freqs, psd = compute_psd(channel_data, sfreq)
            for band, (low, high) in bands.items():
                band_power = np.sum(psd[:, (freqs >= low) & (freqs <= high)], axis=1)
                features[f"{channel}_{band}_power"] = band_power

        # Compute entropy features
        if "entropy" in feature_types:
            samp_entropy = np.array([ent.sample_entropy(ch) for ch in channel_data])
            app_entropy = np.array([ent.app_entropy(ch) for ch in channel_data])
            features[f"{channel}_sample_entropy"] = samp_entropy
            features[f"{channel}_approx_entropy"] = app_entropy
    print(features)
    return features


def main(args):
    # Load the denoised dataset
    input_path = set_path(args.infile)

    epochs = mne.read_epochs(input_path, preload=True)
    logger.info("Denoised data loaded")

    # Extract features from the epochs
    features = extract_features(epochs, args.features)

    # Save the extracted features to a file
    features_output_file = args.outfile
    features_output_path = set_path(features_output_file)
    np.save(features_output_path, features)
    logger.info(f"Extracted features saved to {features_output_path}")
    print(f"Extracted features saved to {features_output_path}")


if __name__ == "__main__":
    USAGE = "Extract features from denoised data"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "--infile",
        "-i",
        type=str,
        help="name of the file to load",
        default="denoised_data-epo.fif",
    )
    parser.add_argument(
        "--outfile",
        "-o",
        type=str,
        help="name of the file to save extracted features",
        default="extracted_features.npy",
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
    main(args)
