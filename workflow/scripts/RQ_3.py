"""
This script loads epochs data from a file, selects a single event type for
comparison, and plots the event-related potential (ERP) for the selected
channels.
Date: 2024-07-02
License: MIT
"""

# How does the event-related potential (ERP) differ across channels such as
# AF3 (frontal), P7 (parietal), and O1 (occipital) for a specific cognitive
# task in the EPOC data?

import mne
import numpy as np
import matplotlib.pyplot as plt
import argparse

from utils import get_path
from logger import configure_logger


def main(infile, outfile, channels, show=False):
    """
    Generate and save an ERP plot for a selected event type and channels.

    Parameters:
    - infile (str): The path to the input file containing epochs data.
    - outfile (str): The path to save the generated plot.
    - channels (list): A list of channel names to plot.
    - show (bool, optional): Whether to display the plot. Default is False.

    Returns:
    - None
    """

    # Configure logger
    logger = configure_logger()

    # Load the epochs data
    infile_path = get_path(infile)
    epochs = mne.read_epochs(infile_path, preload=True)
    logger.info(f"Loaded epochs data from {infile_path}")

    # Get unique event types
    event_ids = np.unique(epochs.events[:, 2])
    # Select a single event type for comparison
    event_id = event_ids[0]

    # initialise the plot
    plt.figure(figsize=(12, 8))

    # Plot the ERP for the selected channels
    erp = epochs[event_id].average()
    for channel in channels:
        plt.plot(
            erp.times,
            erp.data[erp.ch_names.index(channel)],
            label=f"{channel}",
        )

    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (µV)")
    plt.title(f"ERP for Event {event_id} at Selected Channels")
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
        "--channels",
        type=list,
        nargs="+",
        choices=[
            "AF3",
            "F7",
            "F3",
            "FC5",
            "T7",
            "P7",
            "O1",
            "O2",
            "P8",
            "T8",
            "FC6",
            "F4",
            "F8",
            "AF4",
        ],
        default=["AF3", "P7", "O1"],
        help="list of channels to compare ERP across",
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
        channels=args.channels,
        show=args.show,
    )
