"""
Question 1: Which frequency bands show the highest variability across
different events, indicating event-related changes in brain activity?

This script calculates the variability of power spectral density (PSD)
across different frequency bands and events. It loads the epochs data,
calculates the PSD for each band and event, converts the results to a
DataFrame, calculates the variability (standard deviation) across events,
identifies the bands with the highest variability, and plots the variability
for each frequency band.

Usage:
    python RQ_1.py infile outfile [--show]

Arguments:
    infile (str): The input file path of the epochs data.
    outfile (str): The output file path to save the plot.

Options:
    --show (bool): Whether to display the plot. Default is False.

Returns:
    None
"""

import mne
import numpy as np
import pandas as pd
from scipy.signal import welch
import matplotlib.pyplot as plt
import argparse

from utils import get_path
from logger import configure_logger


# Define frequency bands
BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 45),
}


def main(infile, outfile, show=False):
    """
    Calculate the variability of power spectral density (PSD)
    across different frequency bands and events.

    Parameters:
    - infile (str): The input file path of the epochs data.
    - outfile (str): The output file path to save the plot.
    - show (bool): Whether to display the plot.

    Returns:
    None
    """
    # Configure logger
    logger = configure_logger(__name__)

    # Load the epochs data
    epochs_filepath = get_path(infile)
    epochs = mne.read_epochs(epochs_filepath, preload=True)
    logger.info("data loaded")
    sfreq = epochs.info["sfreq"]

    # Calculate PSD for each band and event
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
    logger.info("converted to DataFrame")

    # Calculate variability (standard deviation) across events
    variability = {band: psd_df[band].std(axis=1) for band in psd_df.keys()}

    # Identify bands with highest variability
    max_var = max(
        variability, key=lambda band: variability[band].mean()
    )

    # save output to file
    out_text_path = get_path(outfile.split(".")[0] + ".txt")

    output = f"The frequency band with the highest variability is {max_var}"
    with open(out_text_path, 'a') as f:
        f.write(output)

    for band, var in variability.items():
        output = f"Variability in {band} band: {var.mean()}"
        with open(out_text_path, 'a') as f:
            f.write(output)
    logger.info("output saved to file")

    # Extracting bands and their corresponding variability values
    BANDS = list(variability.keys())
    variability_values = [var.mean() for var in variability.values()]
    logger.info("bands and variability values extracted")

    # Plotting the variability for each frequency band
    plt.figure(figsize=(10, 6))
    plt.bar(BANDS, variability_values, color="skyblue")
    plt.xlabel("Frequency Band")
    plt.ylabel("Variability (Standard Deviation)")
    plt.title("Variability in Frequency Bands Across Different Events")

    if show:
        plt.show()

    try:
        plt.savefig(get_path(outfile))
        logger.info("plot saved")
    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


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
        "outfile",
        type=str,
        help="name of the file to save the filtered data",
    )
    parser.add_argument(
        "--show",
        type=bool,
        default=False,
        help="whether to display the plot",
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile, show=args.show)
