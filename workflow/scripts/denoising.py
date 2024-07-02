"""
This script loads cleaned EEG data from a .fif file, re-references the data to
the average of all channels, and saves the denoised data to a new .fif file.
"""

import argparse

import mne
from logger import configure_logger
from utils import get_path


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
        logger = configure_logger()
        # Load the cleaned dataset
        input_path = get_path(infile)
        epochs = mne.read_epochs(input_path, preload=True)
        logger.info("Artifact filtered data loaded")

        # Re-reference to the average of all channels
        epochs.set_eeg_reference("average", projection=True)
        epochs.apply_proj()

        # Save the denoised data
        output_path = get_path(outfile)
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
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "outfile", type=str, help="name of the file to save the denoised data"
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile)
