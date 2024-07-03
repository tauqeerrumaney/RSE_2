"""
This script loads denoised EEG data from a FIF file,
converts it to raw format for inspection, and saves various plots as PNG files.
"""

import os
import traceback
import argparse

import matplotlib.pyplot as plt
import mne
from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(
        infile,
        epoch_plot_file,
        psd_plot_file,
        evoked_plot_file,
        raw_plot_file):
    """
    Main function to load and plot EEG data.

    Args:
        infile (str): Path to the input file containing EEG epochs.
        epoch_plot_filepath (str): Path to save the epochs plot.
        psd_plot_filepath (str): Path to save the PSD plot.
        evoked_plot_filepath (str): Path to save the evoked response plot.
        raw_plot_filepath (str): Path to save the raw data plot.

    Returns:
        None
    """
    try:
        in_path = get_path(infile)

        logger.info("Reading data from %s", in_path)
        epochs = mne.read_epochs(in_path, preload=True)
        logger.info("Finished reading data")

        # Plot epochs and save
        fig = epochs.plot(
            n_epochs=10,
            n_channels=10,
            scalings="auto",
            show=False)
        fig.savefig(get_path(epoch_plot_file))
        plt.close(fig)
        logger.info("Epochs plot saved to %s", epoch_plot_file)

        # Plot PSD and save
        fig = epochs.compute_psd(
            fmin=0.1,
            fmax=60).plot(
            show=False,
            amplitude=False)
        fig.savefig(get_path(psd_plot_file))
        plt.close(fig)
        logger.info("PSD plot saved to %s", psd_plot_file)

        # Plot evoked response and save
        evoked = epochs.average()
        fig = evoked.plot(show=False)
        fig.savefig(get_path(evoked_plot_file))
        plt.close(fig)
        logger.info("Evoked response plot saved to %s", evoked_plot_file)

        # Convert epochs to raw for inspection
        raw_data = epochs.get_data(copy=True)
        info = epochs.info
        _, n_channels, _ = raw_data.shape

        raw = mne.io.RawArray(raw_data.reshape(n_channels, -1), info)

        # Plot raw data and save
        fig = raw.plot(
            n_channels=len(
                raw.ch_names),
            scalings="auto",
            show=False)
        fig.savefig(get_path(raw_plot_file))
        plt.close(fig)
        logger.info("Raw data plot saved to %s", raw_plot_file)

    except FileNotFoundError as e:
        logger.error(f"Could not find file: {e}")
        logger.debug(traceback.format_exc())
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile",
        type=str,
        help="Name of the file to load.",
    )
    parser.add_argument(
        "epoch_plot_file",
        type=str,
        help="Name of the file to save the epochs plot.",
    )
    parser.add_argument(
        "psd_plot_file",
        type=str,
        help="Name of the file to save the PSD plot.",
    )
    parser.add_argument(
        "evoked_plot_file",
        type=str,
        help="Name of the file to save the evoked response plot.",
    )
    parser.add_argument(
        "raw_plot_file",
        type=str,
        help="Name of the file to save the raw data plot.",
    )

    args = parser.parse_args()
    main(
        infile=args.infile,
        epoch_plot_file=args.epoch_plot_file,
        psd_plot_file=args.psd_plot_file,
        evoked_plot_file=args.evoked_plot_file,
        raw_plot_file=args.raw_plot_file)
