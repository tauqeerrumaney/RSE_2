"""
This script loads bandpass filtered EEG data from a feather file,
 truncates all signals to the length of the shortest signal,
 and saves the truncated data back to a new feather file.

Usage:
    Run the script from the command line with the following options:

    ```
    python truncate_signal.py infile outfile
    ```

    Example:
    ```
    python truncate_signal.py bandpassed_data.feather truncated_data.feather
    ```

Options:
    infile (str): Path to the input file containing the bandpass filter data.
    outfile (str):  Path to the output file where the data is saved.

Files:
    infile: The input file contains bandpass filtered EEG data in the
       feather format.
    outfile: The output file where the truncated data will be saved in
       the feather format.

Functions:
    main(infile, outfile):
        Loads, truncates, and saves EEG signal data.
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
    Main function to load, truncate, and save bandpass data.

    This function reads bandpass filter data from the specified input file,
    truncates the signals to the shortest length found among them, and saves
    the truncated data to the specified output file.

    Args:
        infile (str): Path to the input file containing bandpass filter data
        outfile (str): Path to the outfile to save truncated data.

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
        lambda signal: signal[:target_length]
    )
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
