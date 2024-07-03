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


def main(infile, outfile):
    """
    Main function to load, truncate, and save EEG signal data.

    Args:
        infile (str): The path to the input file containing the bandpass filtered EEG data.
        outfile (str): The path to the output file where truncated data is saved.

    Returns:
        None
    """

    in_path = get_path(infile)

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

    out_path = get_path(outfile)
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
    except ValueError as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
    except FileNotFoundError as e:
        logger.error(f"Could not find file: {e}")
        logger.debug(traceback.format_exc())
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
