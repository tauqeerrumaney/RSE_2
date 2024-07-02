"""
This script generates a plot of kurtosis values for selected channels.
Date: 2024-07-02
License: MIT
"""

# 5. How do the kurtosis values of EEG signals vary across different epochs
# for channels FC6, F4, and F8, and what do these variations reveal about
# the underlying neural dynamics?

import numpy as np
import matplotlib.pyplot as plt
import argparse

from utils import get_path
from logger import configure_logger


def main(infile, outfile, channels, show=False):
    """
    Generate a plot of kurtosis values for selected channels.

    Parameters:
    - infile (str): The path to the input file containing extracted features.
    - outfile (str): The path to save the generated plot.
    - channels (list): A list of channel names to plot kurtosis values for.
    - show (bool, optional): Whether to display the plot. Defaults to False.

    Returns:
    None
    """

    # Configure logger
    logger = configure_logger(__name__)

    # Load the extracted features
    infile_path = get_path(infile)
    features = np.load(infile_path, allow_pickle=True).item()
    logger.info(f"Loaded epochs data from {infile_path}")

    # Plotting kurtosis values for selected channels
    plt.figure(figsize=(10, 6))
    for channel in channels:
        key = f"{channel}_kurtosis"
        if key in features:
            plt.plot(features[key], label=channel)
    plt.title('Kurtosis Values')
    plt.xlabel('Epochs')
    plt.ylabel('Kurtosis')
    plt.legend()
    plt.tight_layout()

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
        default=['FC6', 'F4', 'F8'],
        help="list of channels to compare ERP across",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="whether to display the plot",
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile, channels=args.channels, show=args.show,)
