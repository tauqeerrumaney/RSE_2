"""
This script perform analysis on EEG signals from channels O1 and O2.
"""

# How do the EEG signals from channels O1 and O2 differ during
# various cognitive tasks, and what do these differences reveal about
# lateralized brain activity in the occipital lobe?

import argparse
import os

import matplotlib.pyplot as plt
import mne
import numpy as np
from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))

def main(infile, outfile, show=False):
    """
    Perform analysis on EEG signals from channels O1 and O2.

    Parameters:
        infile (str): Path to the input file containing the epochs data.
        outfile (str): Path to save the output plot.
        show (bool, optional): Whether to display the plot. Defaults to False.

    Returns:
        None
    """
    # Load the epochs data
    in_path = get_path(infile)

    logger.info("Reading data from %s", in_path)
    epochs = mne.read_epochs(in_path, preload=True)
    logger.info("Finished reading data")

    # Get data for channels O1 and O2
    O1_data = epochs.get_data(copy=True)[:, epochs.ch_names.index("O1"), :]
    O2_data = epochs.get_data(copy=True)[:, epochs.ch_names.index("O2"), :]

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

    # Save the plot
    out_path = get_path(outfile)
    plt.savefig(out_path)
    logger.info("Plot saved to %s", out_path)


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
