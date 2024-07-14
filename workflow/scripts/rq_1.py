"""
The script reads EEG epochs data, calculates the PSD across specified
frequency bands for different events, and determines the variability in
these bands. The results are saved as a plot and a JSON file.

Usage:
    Run the script from the command line with the following options:

    ```
    python rq_1.py infile outimage outtext [--show]
    ```

    Example:
    ```
    python rq_1.py denoised_epo.fif rq_1.png rq_1.json --show
    ```

Options:
    infile (str): Path to the input file containing the denoised data.
    outimage (str): Path to save the output plot.
    outtext (str): Path to save the variability data as JSON.
    --show (bool, optional): Whether to display the plot. Default: False

Files:
    infile: The input file contains denoised data in the FIF format.
    outimage: The output file where the plot will be saved in the PNG format.
    outtext: The output file where the variability data will be saved in
             the JSON format.

Functions:
    main(infile, outimage, outtext, show=False):
        Calculates and saves the variability of PSD across different
        frequency bands and events.
    compute_psd(data, sfreq, band):
        Computes the power spectral density (PSD) for a given frequency
        band using Welch's method.
"""

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

    This function reads denoised data from an input file, computes the
    power spectral density (PSD) for different frequency bands and events,
    calculates the variability of these PSDs, and saves the results to output
    files. Optionally, it can display the variability plot.

    Args:
        infile (str): Path to the input file containing the denoised data.
        outimage (str):Path to the output file where the plot will be saved.
        outtext (str): Path to the output file to save the variability data
            as JSON.
        show (bool, optional): Whether to display the plot. Default is False.

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
    if not isinstance(outimage, str):
        raise TypeError(
            f"Expected 'outimage' to be of type str, but got "
            f"{type(outimage).__name__}"
        )
    if not isinstance(outtext, str):
        raise TypeError(
            f"Expected 'outtext' to be of type str, but got "
            f"{type(outtext).__name__}"
        )
    if not isinstance(show, bool):
        raise TypeError(
            f"Expected 'show' to be of type bool, but got "
            f"{type(show).__name__}"
        )

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
    n_epochs = min(len(epochs.events), 100)  # Use at most 100 epochs
    epochs_subset = epochs[:n_epochs]
    logger.info(
        "Finished reading data. Calculating PSD for %d events",
        len(epochs_subset.events),
    )

    # Calculate PSD for each band and event using parallel processing
    sfreq = epochs.info["sfreq"]
    psd_values = {band: [] for band in BANDS}
    for event_id in range(len(epochs_subset.events)):
        epoch_data = epochs_subset[event_id].get_data(copy=True)
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

    This function calculates the PSD of the input data using Welch's method,
    which segments the data, applies a window function to each segment, and
    averages the periodograms of the segments. The function returns the mean
    PSD values within the specified frequency band.

    Args:
        data (array-like): The input data. It can be a 1-D array or
          a 2-D array where each row represents a different channel or trial.
        sfreq (float): The sampling frequency of the input data in Hertz (Hz).
        band (tuple): A tuple specifying the frequency band of interest.
           The tuple should contain two elements: the lower and upper
           frequency bounds in Hz.

    Returns:
        array-like: The mean PSD values within the specified frequency band.
           If the input data is a 2-D array, the returned array will contain
           the mean PSD values for each row (channel/trial).

    Raises:
        ValueError: If the input data is not array-like or if the band is
           not a tuple with two elements.
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
