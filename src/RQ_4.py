"""
This script analyzes the spectrograms of channels F3 and FC6 during
cognitive tasks to understand the brain's response in the frontal
and frontal-central regions.

Usage:
    python RQ_4.py infile outfile [--channels CHANNELS] [--show SHOW]

Arguments:
    infile (str): Name of the file to load the epochs data from.
    outfile (str): Name of the file to save the plot.

Options:
    --channels (list): List of channels to compare ERP across.
        Default: ["F3", "FC6"]
    --show (bool): Whether to display the plot. Default: False
"""

import mne
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import numpy as np
import argparse

from utils import get_path
from logger import configure_logger


def main(infile, outfile, channels, show=False):
    """
    Generate spectrograms for the specified channels and save the plot to an output file.

    Parameters:
    - infile (str): Path to the input file containing epochs data.
    - outfile (str): Path to the output file where the plot will be saved.
    - channels (list): Channel names for which spectrograms will be generated.
    - show (bool, optional): Whether to display the plot. Defaults to False.

    Returns:
    None
    """
    
    # Configure logger
    logger = configure_logger(__name__)

    # Load the epochs data
    infile_path = get_path(infile)
    epochs = mne.read_epochs(infile_path, preload=True)
    logger.info(f"Loaded epochs data from {infile_path}")

    sfreq = epochs.info['sfreq']

    # Plot spectrograms for the two important channels in one plot
    fig, axs = plt.subplots(1, 2, figsize=(20, 6))

    for i, channel_name in enumerate(channels):
        channel_index = epochs.ch_names.index(channel_name)
        # Ensure copy is explicitly set
        channel_data = epochs.get_data(copy=True)[:, channel_index, :]
        flattened_data = channel_data.flatten()
        cax = plot_spectrogram(flattened_data, sfreq, channel_name, axs[i])
        logger.info(f"Plotted spectrogram for {channel_name}")

    fig.colorbar(cax, ax=axs, orientation='vertical', label='Power/Frequency (dB/Hz)',)

    if show:
        plt.show()

    try:
        plt.savefig(get_path(outfile))
        logger.info("plot saved")
    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


def plot_spectrogram(data, sfreq, channel_name, ax):
    """Function to plot spectrogram for a given channel"""
    f, t, Sxx = spectrogram(data, fs=sfreq)
    cax = ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
    ax.set_ylabel('Frequency [Hz]')
    ax.set_xlabel('Time [s]')
    ax.set_title(f'Spectrogram for {channel_name}')
    return cax


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
        default=["F3", "FC6"],
        help="list of channels to compare ERP across",
    )
    parser.add_argument(
        "--show",
        type=bool,
        default=False,
        help="whether to display the plot",
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile, channels=args.channels, show=args.show)
