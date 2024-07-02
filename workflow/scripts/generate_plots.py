"""
This script loads denoised EEG data from a FIF file, converts it to raw format for inspection, and saves various plots as PNG files.
"""

import argparse

import matplotlib.pyplot as plt
import mne
from logger import configure_logger
from utils import get_path


def main(infile, directory):
    """
    Main function to load and plot EEG data.

    Args:
        infile (str): Name of the file to load.
        directory (str): Name of the directory to save plots to.

    Returns:
        None
    """
    try:
        logger = configure_logger()
        input_path = get_path(infile)

        epochs = mne.read_epochs(input_path, preload=True)

        # Convert epochs to raw for inspection
        raw_data = epochs.get_data()
        info = epochs.info
        n_epochs, n_channels, n_times = raw_data.shape

        raw = mne.io.RawArray(raw_data.reshape(n_channels, -1), info)

        # Plot raw data and save
        fig = raw.plot(n_channels=len(raw.ch_names), scalings="auto", show=False)
        fig.savefig(get_path(f"{directory}/raw_data.png"))
        plt.close(fig)

        # Plot epochs and save
        fig = epochs.plot(n_epochs=10, n_channels=10, scalings="auto", show=False)
        fig.savefig(get_path(f"{directory}/epochs_data.png"))
        plt.close(fig)

        # Plot PSD and save
        fig = epochs.plot_psd(fmin=0.1, fmax=60, show=False)
        fig.savefig(get_path(f"{directory}/epochs_psd.png"))
        plt.close(fig)

        # Plot evoked response and save
        evoked = epochs.average()
        fig = evoked.plot(show=False)
        fig.savefig(get_path(f"{directory}/evoked_response.png"))
        plt.close(fig)

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile",
        type=str,
        help="Name of the file to load.",
    )

    parser.add_argument(
        "directory",
        type=str,
        help="Name of the directory to save plots to.",
    )

    args = parser.parse_args()
    main(infile=args.infile, directory=args.directory)
