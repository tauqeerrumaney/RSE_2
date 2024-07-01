"""
Script for truncating EEG signal data to a uniform length.

This script loads bandpass filtered EEG data from a feather file,
truncates all signals to the length of the shortest signal, and saves
the truncated data back to a new feather file.

Usage:
    python script.py infile outfile

Positional Arguments:
    infile      Name of the file to load.
    outfile     Name of the file to save the truncated data.

Modules Required:
    - pandas
    - argparse
    - utils (providing get_path function)
    - logger (providing configure_logger function)

Functions:
    main(args): Main function to execute the script logic.

Example:
    python script.py filtered_data.feather truncated_data.feather
"""

import pandas as pd
import argparse
from utils import get_path
from logger import configure_logger


def main(infile, outfile):
    """
    Main function to load, truncate, and save EEG signal data.

    This function performs the following steps:
    1. Loads the bandpass filtered EEG data from the specified input file.
    2. Truncates all signals to the length of the shortest signal.
    3. Validates that all signals are truncated to the target length.
    4. Saves the truncated data to the specified output file.

    Args:
        args: Command-line arguments parsed by argparse.

    Returns:
        None
    """
    try:
        logger = configure_logger(__name__)
        file_path = get_path(infile)

        df = pd.read_feather(file_path)
        logger.info("Bandpass filtered data loaded")

        target_length = min(df["size"])

        # Truncate all signals to the target length
        truncated_signals = df["signal"].apply(
            lambda signal: signal[:target_length]
        )
        df["signal"] = truncated_signals
        logger.info("All signals truncated to the target length")

        # Validate that all signals are of the target length
        if not all(df["signal"].apply(len) == target_length):
            raise ValueError(f"Not all signals are of length {target_length}")

        df["size"] = target_length
        logger.info(f"Size adjusted to {target_length}")

        output_file_path = get_path(outfile)
        df.to_feather(output_file_path)

        print(f"Truncated data saved to {output_file_path}")
        logger.info(f"Truncated data saved to {output_file_path}")

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        print(f"ValueError: {ve}")
    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
        print(f"FileNotFoundError: {fnf_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")


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
        help="name of the file to save the truncated data"
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile)
