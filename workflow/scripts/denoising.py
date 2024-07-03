"""
This script loads cleaned EEG data from a .fif file, re-references the data to
the average of all channels, and saves the denoised data to a new .fif file.
"""

import argparse
import os
import traceback

import mne
from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile, outfile):
    """
    Main function to load, process, and save EEG data.

    Args:
        infile (str): Name of the file to load.
        outfile (str): Name of the file to save the denoised data.

    Returns:
        None
    """
    try:
        # Load the cleaned dataset
        in_path = get_path(infile)

        logger.info("Reading data from %s", in_path)
        epochs = mne.read_epochs(in_path, preload=True)
        logger.info("Finished reading data. Applying re-referencing")

        # Re-reference to the average of all channels
        epochs.set_eeg_reference("average", projection=True)
        epochs.apply_proj()

        # Save the denoised data
        out_path = get_path(outfile)
        epochs.save(out_path, overwrite=True)
        logger.info("Denoised data saved to %s", out_path)

    except FileNotFoundError as e:
        logger.error(f"Could not find file: {e}")
        logger.debug(traceback.format_exc())
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "outfile", type=str, help="name of the file to save the denoised data"
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile)
