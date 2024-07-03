"""
This script loads epochs data from a file, selects a single event type for
comparison, and plots the event-related potential (ERP) for the selected
channels.
"""

# How does the event-related potential (ERP) differ across channels such as
# AF3 (frontal), P7 (parietal), and O1 (occipital) for a specific cognitive
# task in the EPOC data?

import argparse
import os

import matplotlib.pyplot as plt
import mne
import numpy as np
from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))

def main(infile, outfile, channels, show=False):
    """
    Generate and save an ERP plot for a selected event type and channels.

    Parameters:
        infile (str): The path to the input file containing epochs data.
        outfile (str): The path to save the generated plot.
        channels (list): A list of channel names to plot.
        show (bool, optional): Whether to display the plot. Default is False.

    Returns:
        None
    """
    # Load the epochs data
    in_path = get_path(infile)

    logger.info("Reading data from %s", in_path)
    epochs = mne.read_epochs(in_path, preload=True)
    logger.info("Finished reading data")

    # Get unique event types
    event_ids = np.unique(epochs.events[:, 2])
    # Select a single event type for comparison
    event_id = event_ids[0]

    # initialise the plot
    plt.figure(figsize=(12, 8))

    # Plot the ERP for the selected channels
    logger.info("Plotting ERP for event %d at channels %s", event_id, channels)
    
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
