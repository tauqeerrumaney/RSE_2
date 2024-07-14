"""
The script reads EEG epochs data, generates plots for epochs,
power spectral density (PSD), evoked response, and raw data,
and saves these plots to specified files.

Usage:
    Run the script from the command line with the following options:

    ```
    python generate_plots.py infile epoch_plot_file psd_plot_file
    evoked_plot_file raw_plot_file
    ```

    Example:
    ```
    python generate_plots.py denoised_epo.fif denoised_epo_epochs.png
    denoised_epo_psd.png denoised_epo_response.png denoised_epo_raw.png
    ```

Options:
    infile (str): Path to the input file contains denoised data.
    epoch_plot_file (str): Path to save the epochs plot.
    psd_plot_file (str): Path to save the PSD plot.
    evoked_plot_file (str): Path to save the evoked response plot.
    raw_plot_file (str): Path to save the raw data plot.

Files:
    infile: The input file contains denoised data in the FIF format.
    epoch_plot_file: The output file where the epochs plot will be saved in
        PNG format.
    psd_plot_file: The output file where the PSD plot will be saved in
        PNG format.
    evoked_plot_file: The output file where the evoked response plot
        be saved  in PNG format.
    raw_plot_file: The output file where the raw data plot will be saved in
       PNG format.

Functions:
    main(infile, epoch_plot_file, psd_plot_file, evoked_plot_file,
    raw_plot_file):
        Generates and saves plots for epochs, PSD, evoked response,
        and raw data.
"""

import argparse
import os
import traceback

import matplotlib.pyplot as plt
import mne

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(
    infile: str,
    epoch_plot_file: str,
    psd_plot_file: str,
    evoked_plot_file: str,
    raw_plot_file: str,
):
    """
    Main function to load and plot EEG data.

    This function loads denoised EEG epochs from an input file, generate plots
    for epochs, power spectral density (PSD), evoked responses, and raw data,
    and saves these plots to specified output files.

    Args:
        infile (str): Path to the input file containing the denoised data.
        epoch_plot_file (str): Path to save the epochs plot.
        psd_plot_file (str): Path to save the PSD plot.
        evoked_plot_file (str): Path to save the evoked response plot.
        raw_plot_file (str): Path to save the raw data plot.

    Returns:
        None

    Raises:
        FileNotFoundError: If the input file does not exist.
        TypeError: If the input parameters are not of the expected types.
    """
    # Validate input types
    if not isinstance(infile, str):
        raise TypeError(
            f"Expected 'infile' to be of type str, but got "
            f"{type(infile).__name__}"
        )
    if not isinstance(epoch_plot_file, str):
        raise TypeError(
            f"Expected 'epoch_plot_file' to be of type str, but got "
            f"{type(epoch_plot_file).__name__}"
        )
    if not isinstance(psd_plot_file, str):
        raise TypeError(
            f"Expected 'psd_plot_file' to be of type str, but got "
            f"{type(psd_plot_file).__name__}"
        )
    if not isinstance(evoked_plot_file, str):
        raise TypeError(
            f"Expected 'evoked_plot_file' to be of type str, but got "
            f"{type(evoked_plot_file).__name__}"
        )
    if not isinstance(raw_plot_file, str):
        raise TypeError(
            f"Expected 'raw_plot_file' to be of type str, but got "
            f"{type(raw_plot_file).__name__}"
        )

    # Validate input file
    in_path = get_path(infile)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    # Load epochs
    logger.info("Reading data from %s", in_path)
    epochs = mne.read_epochs(in_path, preload=True)
    logger.info("Finished reading data")

    # Plot epochs and save
    fig = epochs.plot(n_epochs=10, n_channels=10, scalings="auto", show=False)
    fig.savefig(get_path(epoch_plot_file))
    plt.close(fig)
    logger.info("Epochs plot saved to %s", epoch_plot_file)

    # Plot PSD and save
    fig = epochs.compute_psd(fmin=0.1, fmax=60).plot(
        show=False, amplitude=False
    )
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
    fig = raw.plot(n_channels=len(raw.ch_names), scalings="auto", show=False)
    fig.savefig(get_path(raw_plot_file))
    plt.close(fig)
    logger.info("Raw data plot saved to %s", raw_plot_file)


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
    try:
        main(
            infile=args.infile,
            epoch_plot_file=args.epoch_plot_file,
            psd_plot_file=args.psd_plot_file,
            evoked_plot_file=args.evoked_plot_file,
            raw_plot_file=args.raw_plot_file,
        )
    except (TypeError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
