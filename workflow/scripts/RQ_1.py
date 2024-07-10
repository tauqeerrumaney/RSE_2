"""
This script calculates the variability of power spectral density (PSD)
across different frequency bands and events.
"""

# Question 1: Which frequency bands show the highest variability across
# different events, indicating event-related changes in brain activity?

import argparse
import json
import os
import traceback

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from scipy.signal import welch

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))

# Define frequency bands
BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 45),
}


def main(infile: str, outimage: str, outtext: str, show: bool = False):
    """
    Calculate the variability of power spectral density (PSD)
    across different frequency bands and events.

    Parameters:
        infile (str): The input file path of the epochs data.
        outimage (str): The output file path to save the plot.
        outtext (str): The output file path to save the variability data
          as JSON.
        show (bool): Whether to display the plot.

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
            f"{type(infile).__name__}")
    if not isinstance(outimage, str):
        raise TypeError(
            f"Expected 'outimage' to be of type str, but got "
            f"{type(outimage).__name__}")
    if not isinstance(outtext, str):
        raise TypeError(
            f"Expected 'outtext' to be of type str, but got "
            f"{type(outtext).__name__}")
    if not isinstance(show, bool):
        raise TypeError(
            f"Expected 'show' to be of type bool, but got "
            f"{type(show).__name__}")

    # Validate input file
    in_path = get_path(infile)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    # Validate output files
    out_img_path = get_path(outimage)
    out_text_path = get_path(outtext)

    out_img_dir = os.path.dirname(out_img_path)
    out_text_dir = os.path.dirname(out_text_path)
    if out_img_dir and not os.path.exists(out_img_dir):
        raise ValueError(f"Output directory does not exist: {out_img_dir}")
    if out_text_dir and not os.path.exists(out_text_dir):
        raise ValueError(f"Output directory does not exist: {out_text_dir}")

    # Load the epochs data
    logger.info("Reading data from %s", in_path)
    epochs = mne.read_epochs(in_path, preload=True)
    logger.info(
        "Finished reading data. Calculating PSD for %d events", len(
            epochs.events))

    # Calculate PSD for each band and event
    sfreq = epochs.info["sfreq"]
    psd_values = {band: [] for band in BANDS}
    for event_id in range(len(epochs.events)):
        epoch_data = epochs[event_id].get_data(copy=True)
        for band, freq_range in BANDS.items():
            psd_band_values = []
            for channel_data in epoch_data:
                psd_band_values.append(
                    compute_psd(channel_data, sfreq, freq_range)
                )
            psd_values[band].append(np.array(psd_band_values).mean(axis=0))

    logger.info("PSD calculated for each band and event")

    # Convert to DataFrame for easier analysis
    psd_df = {
        band: pd.DataFrame(psd_values[band]) for band in psd_values.keys()
    }

    # Calculate variability (standard deviation) across events
    variability = {band: psd_df[band].std(axis=1) for band in psd_df.keys()}

    # Identify bands with highest variability
    max_var = max(variability, key=lambda band: variability[band].mean())

    output_data = {
        "max_var_band": max_var,
        "variability": {band: var.mean() for band, var in variability.items()},
    }
    with open(out_text_path, "w") as f:
        json.dump(output_data, f, indent=4)
    logger.info("Variability data saved to %s", out_text_path)

    # Extracting bands and their corresponding variability values
    freq_bands = list(variability.keys())
    variability_values = [var.mean() for var in variability.values()]
    logger.info("Bands and variability values extracted for plotting")

    # Plotting the variability for each frequency band
    plt.figure(figsize=(10, 6))
    plt.bar(freq_bands, variability_values, color="skyblue")
    plt.xlabel("Frequency Band")
    plt.ylabel("Variability (Standard Deviation)")
    plt.title("Variability in Frequency Bands Across Different Events")
    plt.savefig(out_img_path)
    logger.info("Plot saved to %s", out_img_path)

    if show:
        plt.show()


def compute_psd(data, sfreq, band):
    """
    Compute the power spectral density (PSD) for a given frequency band
    using Welch's method.

    Parameters:
        data (array-like): The input data.
        sfreq (float): The sampling frequency of the data.
        band (tuple): The frequency band of interest.

    Returns:
        array-like: The mean PSD values within the specified frequency band.
    """
    freqs, psd = welch(data, sfreq, nperseg=248)
    band_freqs = (freqs >= band[0]) & (freqs <= band[1])
    return np.mean(psd[:, band_freqs], axis=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile",
        type=str,
        help="name of the file to load",
    )
    parser.add_argument(
        "outimage",
        type=str,
        help="name of the file to save the image",
    )
    parser.add_argument(
        "outtext",
        type=str,
        help="name of the file to save the output json",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="whether to display the plot",
    )

    args = parser.parse_args()
    try:
        main(
            infile=args.infile,
            outimage=args.outimage,
            outtext=args.outtext,
            show=args.show,
        )
    except (TypeError, ValueError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
