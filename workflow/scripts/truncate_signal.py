"""
This script loads bandpass filtered EEG data from a feather file,
truncates all signals to the length of the shortest signal, and saves
the truncated data back to a new feather file.
"""

import argparse
import os
import traceback

import pandas as pd

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile: str, outfile: str):
    """
    Main function to load, truncate, and save EEG signal data.

    Args:
        infile (str): The path to the input file containing EEG data.
        outfile (str): The path of the file to save truncated data to.

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

    # Validate input file
    in_path = get_path(infile)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    # Validate output file
    out_path = get_path(outfile)
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        raise ValueError(f"Output directory does not exist: {out_dir}")

    # Read the data from the input file
    logger.info("Reading data from %s", in_path)
    df = pd.read_feather(in_path)
    logger.info("Finished reading data. Truncating signals")

    target_length = min(df["size"])

    # Truncate all signals to the target length
    truncated_signals = df["signal"].apply(
        lambda signal: signal[:target_length])
    df["signal"] = truncated_signals
    logger.info("All signals truncated to length %d", target_length)

    df["size"] = target_length

    df.to_feather(out_path)

    logger.info("Truncated data saved to %s", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "outfile", type=str, help="name of the file to save the truncated data"
    )

    args = parser.parse_args()
    try:
        main(infile=args.infile, outfile=args.outfile)
    except (TypeError, ValueError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
