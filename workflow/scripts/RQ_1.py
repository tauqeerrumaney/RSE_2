"""
This script calculates the variability of power spectral density (PSD)
across different frequency bands and events.
"""

# Question 1: Which frequency bands show the highest variability across
# different events, indicating event-related changes in brain activity?

import argparse
import json
import os

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from logger import configure_logger
from scipy.signal import welch
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


def main(infile, outimage, outtext, show=False):
    """
    Calculate the variability of power spectral density (PSD)
    across different frequency bands and events.

    Parameters:
        infile (str): The input file path of the epochs data.
        outfile (str): The output file path to save the plot.
        show (bool): Whether to display the plot.

    Returns:
        None
    """
    # Load the epochs data
    in_path = get_path(infile)

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

    # save output to file
    out_text_path = get_path(outtext)

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

    if show:
        plt.show()

    out_img_path = get_path(outimage)
    plt.savefig(out_img_path)
    logger.info("Plot saved to %s", out_img_path)


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
    main(
        infile=args.infile,
        outimage=args.outimage,
        outtext=args.outtext,
        show=args.show,
    )
