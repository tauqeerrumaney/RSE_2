"""
This script generates a plot of kurtosis values for selected channels.
"""

# 5. How do the kurtosis values of EEG signals vary across different epochs
# for channels FC6, F4, and F8, and what do these variations reveal about
# the underlying neural dynamics?

import argparse
import os
import traceback

import matplotlib.pyplot as plt
import numpy as np

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile: str, outfile: str, channels: list[str], show: bool = False):
    """
    Generate a plot of kurtosis values for selected channels.

    Parameters:
        infile (str): The path to the input file containing extracted features.
        outfile (str): The path to save the generated plot.
        channels (list): A list of channel names to plot kurtosis values for.
        show (bool, optional): Whether to display the plot. Defaults to False.

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
    if not isinstance(outfile, str):
        raise TypeError(
            f"Expected 'outfile' to be of type str, but got "
            f"{type(outfile).__name__}"
        )
    if not isinstance(channels, list):
        raise TypeError(
            f"Expected 'channels' to be of type list, but got "
            f"{type(channels).__name__}"
        )
    if not all(isinstance(channel, str) for channel in channels):
        raise TypeError(
            "Expected all elements in 'channels' to be of type str"
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

    # Validate output file
    out_path = get_path(outfile)
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        raise ValueError(f"Output directory does not exist: {out_dir}")

    logger.info("Reading data from %s", in_path)
    features = np.load(in_path, allow_pickle=True).item()
    logger.info("Finished reading data")

    # Plotting kurtosis values for selected channels
    logger.info("Plotting kurtosis values for channels %s", channels)
    plt.figure(figsize=(10, 6))
    for channel in channels:
        key = f"{channel}_kurtosis"
        if key in features:
            plt.plot(features[key], label=channel)
    plt.title("Kurtosis Values")
    plt.xlabel("Epochs")
    plt.ylabel("Kurtosis")
    plt.legend()
    plt.tight_layout()

    # Save the plot
    plt.savefig(out_path)
    logger.info("Plot saved to %s", out_path)

    if show:
        plt.show()


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
        default=["FC6", "F4", "F8"],
        help="list of channels to compare ERP across",
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
            outfile=args.outfile,
            channels=args.channels,
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
