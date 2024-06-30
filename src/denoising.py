"""
Script for loading, referencing, and saving EEG data.

This script loads cleaned EEG data from a .fif file, re-references the data to
the average of all channels, and saves the denoised data to a new .fif file.

Usage:
    python script.py infile outfile

Positional Arguments:
    infile      Name of the file to load.
    outfile     Name of the file to save the denoised data.

Description:
    The script performs the following steps:
    1. Loads the cleaned EEG data from the specified input file.
    2. Re-references the EEG data to the average of all channels.
    3. Saves the denoised data to the specified output file.

Modules Required:
    - mne
    - argparse
    - utils (providing logger and get_path functions)

Functions:
    main(args): Main function to execute the script logic.

Example:
    python script.py cleaned_data-epo.fif denoised_data-epo.fif
"""

import mne
import argparse
from utils import get_path
from logger import configure_logger


def main(infile, outfile):
    """
    Main function to load, process, and save EEG data.

    Args:
        args: Command-line arguments parsed by argparse.

    Returns:
        None
    """
    try:
        logger = configure_logger(__name__)
        # Load the cleaned dataset
        input_path = get_path(infile, folder="data")
        epochs = mne.read_epochs(input_path, preload=True)
        logger.info("Artifact filtered data loaded")

        # Re-reference to the average of all channels
        epochs.set_eeg_reference("average", projection=True)
        epochs.apply_proj()

        # Save the denoised data
        output_path = get_path(outfile, folder="data")
        epochs.save(output_path, overwrite=True)
        logger.info(f"Denoised data saved to {output_path}")
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
        help="name of the file to load"
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="name of the file to save the denoised data"
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile)
