"""
This script loads cleaned EEG data from a .fif file, re-references the data
to the average of all channels, and saves the denoised data to a new file.

Usage:
    Run the script from the command line with the following options:

    ```
    python denoising.py infile outfile
    ```

    Example:
    ```
    python denoising.py cleaned_epo.fif denoised_epo.fif
    ```

Options:
    infile (str): Path to the input file containing cleaned EEG data.
    outfile (str): Path to save the denoised EEG data.

Files:
    infile: The input file contains cleaned EEG data in the FIF format.
    outfile: The output file where the denoised EEG data will be saved
        in the FIF format.

Functions:
    main(infile, outfile):
        Loads the EEG data from the input file, applies re-referencing,
        and saves the denoised data to the output file
"""

import argparse
import os
import traceback

import mne

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile: str, outfile: str):
    """
    Main function to load, process, and save EEG data.

    This function reads EEG data from an input file, applies re-referencing
    to the average of all channels, and saves the denoised data to an
    output file.

    Args:
        infile (str): Path to the input file containing cleaned EEG data.
        outfile (str): Path to the output file where the denoised EEG data
            will be saved.

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
    if not isinstance(outfile, str):
        raise TypeError(
            f"Expected 'outfile' to be of type str, but got "
            f"{type(outfile).__name__}"
        )

    # Validate input file
    in_path = get_path(infile)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    # Load the epochs
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "outfile", type=str, help="name of the file to save the denoised data"
    )

    args = parser.parse_args()
    try:
        main(infile=args.infile, outfile=args.outfile)
    except (TypeError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
