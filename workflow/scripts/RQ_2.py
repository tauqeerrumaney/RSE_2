"""
This script performs analysis on EEG signals from channels O1 and O2.
Date: 2024-07-02
License: MIT
"""

# How do the EEG signals from channels O1 and O2 differ during
# various cognitive tasks, and what do these differences reveal about
# lateralized brain activity in the occipital lobe?

import mne
import numpy as np
import matplotlib.pyplot as plt
import argparse

from utils import get_path
from logger import configure_logger


def main(infile, outfile, show=False):
    """
    Perform analysis on EEG signals from channels O1 and O2.

    Parameters:
    - infile (str): Path to the input file containing the epochs data.
    - outfile (str): Path to save the output plot.
    - show (bool, optional): Whether to display the plot. Defaults to False.
    """

    # Configure logger
    logger = configure_logger()

    # Load the epochs data
    infile_path = get_path(infile)
    epochs = mne.read_epochs(infile_path, preload=True)

    # Get data for channels O1 and O2
    O1_data = epochs.get_data()[:, epochs.ch_names.index("O1"), :]
    O2_data = epochs.get_data()[:, epochs.ch_names.index("O2"), :]

    # Compute the average across epochs for comparison
    O1_avg = np.mean(O1_data, axis=0)
    O2_avg = np.mean(O2_data, axis=0)

    # Plot the comparison between O1 and O2
    plt.figure(figsize=(12, 6))
    plt.plot(O1_avg, label="O1")
    plt.plot(O2_avg, label="O2")
    plt.xlabel("Time (samples)")
    plt.ylabel("Amplitude")
    plt.title("Comparison of EEG Signals from Channels O1 and O2")
    plt.legend()

    if show:
        plt.show()

    try:
        plt.savefig(get_path(outfile))
        logger.info("plot saved")
    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


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
        action="store_true",
        help="whether to display the plot",
    )

    args = parser.parse_args()
    main(
        infile=args.infile,
        outfile=args.outfile,
        show=args.show,
    )
