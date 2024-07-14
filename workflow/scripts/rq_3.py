"""
This script analyzes event-related potential (ERP) differences across specific
EEG channels and saves the plot.

Usage:
    Run the script from the command line with the following options:

    ```
    python rq_3.py infile outfile [--channels CHANNELS] [--show]
    ```

    Example:
    ```
    python rq_3.py denoised_epo.fif rq_3.png --channels AF3 P7 O1 --show
    ```

Options:
    infile (str): Path to the input file containing the denoised data.
    outfile (str): Path to save the output plot.
    --channels (list of str, optional): List of channels to compare ERP across.
        Default: ["AF3", "P7", "O1"]
    --show (bool, optional): Whether to display the plot. Default: False

Files:
    infile: The input file contains denoised data in the FIF format.
    outfile: The output file where the plot will be saved in the PNG format.

Functions:
    main(infile, outfile, channels, show=False):
        Generates and saves an ERP plot for a selected event type and
        channels.
"""

import argparse
import os
import traceback

import matplotlib.pyplot as plt
import mne
import numpy as np
from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile: str, outfile: str, channels: list[str], show=False):
    """
    Generate and save an ERP plot for a selected event type and channels.

    This function reads denoised data from an input file, generates an
    Event-Related Potential (ERP) plot for a specified event type and
    selected channels, and saves the plot to an output file. Optionally,
    the plot can be displayed.

    Args:
        infile (str): Path to the input file containing the denoised data.
        outfile (str): Path to save the output plot.
        channels (list of str, optional): A list of channel names to plot.
           Default: ["AF3", "P7", "O1"]
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

    # Load the epochs data
    logger.info("Reading data from %s", in_path)
    epochs = mne.read_epochs(in_path, preload=True)
    logger.info("Finished reading data")

    # Get unique event types
    event_ids = np.unique(epochs.events[:, 2])
    # Select a single event type for comparison
    event_id = event_ids[0]

    # Initialise the plot
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
        help="Path to the input file containing epochs data.",
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="Path to save the generated plot.",
    )
    parser.add_argument(
        "--channels",
        type=str,
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
        help="List of channels to compare ERP across.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Whether to display the plot.",
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
