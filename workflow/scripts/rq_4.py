"""
This script generates spectrograms for the specified channels
and saves the plot.

Usage:
    Run the script from the command line with the following options:

    ```
    python  rq_4.py infile outfile [--channels CHANNELS] [--show]
    ```

    Example:
    ```
    python rq_4.py denoised_epo.fif rq_4.png --channels F3 FC6 --show
    ```

Options:
    infile (str): Path to the input file containing denoised data.
    outfile (str): Path to save the output plot.
    --channels (list of str, optional): List of channels for which to generate
       spectrograms. Default: ["F3", "FC6"]
    --show (bool, optional): Whether to display the plot. Default: False

Files:
    infile: The input file containing the denoised data in the FIF format.
    outfile: The output file where the plot will be saved in the PNG format.

Functions:
    main(infile, outfile, channels, show=False):
        Generates and saves spectrograms for the specified channels.
    plot_spectrogram(data, sfreq, channel_name, ax):
        Plots a spectrogram of the given data.
"""

import argparse
import os
import traceback

import matplotlib.pyplot as plt
import mne
import numpy as np
from scipy.signal import spectrogram

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile: str, outfile: str, channels: list[str], show: bool = False):
    """
    Generate spectrograms for the specified channels and save the plot to
    an output file.

    This function reads denoised data from an input file in FIF format,
    generates spectrograms for the specified channels, and saves the plot
    to the specified output file. Optionally, it can display the plot.

    Args:
        infile (str): Path to the input file containing the denoised data.
        outfile (str): Path to save the output plot.
        channels (list of str, optional): Channel names for which to generate
           spectrograms.Default: ["F3", "FC6"]
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

    # Load the epochs data
    logger.info("Reading data from %s", in_path)
    epochs = mne.read_epochs(in_path, preload=True)
    logger.info("Finished reading data")

    sfreq = epochs.info["sfreq"]

    # Plot spectrograms for the two important channels in one plot
    fig, axs = plt.subplots(1, 2, figsize=(20, 6))

    for i, channel_name in enumerate(channels):
        logger.info("Plotting spectrogram for channel %s", channel_name)

        channel_index = epochs.ch_names.index(channel_name)
        # Ensure copy is explicitly set
        channel_data = epochs.get_data(copy=True)[:, channel_index, :]
        flattened_data = channel_data.flatten()
        cax = plot_spectrogram(
            flattened_data,
            sfreq,
            channel_name,
            axs[i],
        )

    fig.colorbar(
        cax,
        ax=axs,
        orientation="vertical",
        label="Power/Frequency (dB/Hz)",
    )

    plt.savefig(out_path)
    logger.info("Plot saved to %s", out_path)

    if show:
        plt.show()


def plot_spectrogram(data, sfreq, channel_name, ax):
    """
    Plot a spectrogram of the given data.

    This function computes and plots a spectrogram of the given data
    on the specified axes.

    Args:
        data (numpy.ndarray): The input data array.
        sfreq (int): The sampling frequency of the data.
        channel_name (str): The name of the channel.
        ax (matplotlib.axes.Axes): The axes object to plot the spectrogram on.

    Returns:
        matplotlib.collections.QuadMesh: The QuadMesh object representing the
            spectrogram plot.
    """

    f, t, Sxx = spectrogram(data, fs=sfreq)  # Compute the spectrogram

    # Graph the spectrogram
    cax = ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading="gouraud")
    ax.set_ylabel("Frequency [Hz]")
    ax.set_xlabel("Time [s]")
    ax.set_title(f"Spectrogram for {channel_name}")
    return cax


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
        default=["F3", "FC6"],
        help="List of channels for which to generate spectrograms.",
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
