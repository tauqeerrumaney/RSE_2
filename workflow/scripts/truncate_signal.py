"""
This script loads bandpass filtered EEG data from a feather file,
truncates all signals to the length of the shortest signal, and saves
the truncated data back to a new feather file.
"""

import argparse

import pandas as pd
from logger import configure_logger
from utils import get_path


def main(infile, outfile):
    """
    Main function to load, truncate, and save EEG signal data.

    Args:
        infile (str): The path to the input file containing the bandpass filtered EEG data.
        outfile (str): The path to the output file where truncated data is saved.

    Returns:
        None
    """

    logger = configure_logger()
    file_path = get_path(infile)

    df = pd.read_feather(file_path)
    logger.info("Bandpass filtered data loaded")

    target_length = min(df["size"])

    # Truncate all signals to the target length
    truncated_signals = df["signal"].apply(lambda signal: signal[:target_length])
    df["signal"] = truncated_signals
    logger.info("All signals truncated to the target length")

    # Validate that all signals are of the target length
    if not all(df["signal"].apply(len) == target_length):
        raise ValueError(f"Not all signals are of length {target_length}")

    df["size"] = target_length
    logger.info(f"Size adjusted to {target_length}")

    output_file_path = get_path(outfile)
    df.to_feather(output_file_path)

    logger.info(f"Truncated data saved to {output_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "outfile", type=str, help="name of the file to save the truncated data"
    )

    args = parser.parse_args()
    logger = configure_logger()
    try:
        main(infile=args.infile, outfile=args.outfile)
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")

    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
