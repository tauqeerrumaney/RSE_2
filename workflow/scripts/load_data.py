"""
This script allows EEG data in a .txt file (in a specific format) to be
loaded, converted into micro Volts based on the input resolution and
saved into a smaller data format.

Usage:
    Run the script from the command line with the following options:

    ```
    python data_load.py infile outfile [--mock]
    ```

    Example:
    ```
    python data_load.py EPOC.txt filtered_data.feather --mock
    ```

Options:
    infile (str): Path to the input file containing the raw EEG data.
    outfile (str): Path to the output file where the data is saved.
    --mock (bool, optional): Whether to use a subset of the data for
        testing purposes.

Files:
    infile: The input file contains rows for id, event, device, channel, code,
        size, data; in tsv format.
    outfile: The output file where the filtered data will be saved in
        feather format.

Functions:
    main(infile, outfile, mock=False):
        Loads, processes, and saves EEG data.
"""

import argparse
import os
import traceback

import numpy as np
import pandas as pd

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))

MOCK_SIZE = 10000


def main(infile: str, outfile: str, mock: bool = False):
    """
    Main function to load, process, and save EEG data.

    This function reads raw EEG data from an input file, converts the signal
    values to micro Volts based on a predefined conversion factor, and saves
    the processed data into a feather file format. Optionally, a subset of
    the data can be used for testing purposes.

    Args:
        infile (str): Path to the input file containing the raw EEG data.
        outfile (str): Path to the output file where the data is saved.
        mock (bool): Whether to use a subset of the data for testing purposes.

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
    if not isinstance(mock, bool):
        raise TypeError(
            f"Expected 'mock' to be of type bool, but got "
            f"{type(mock).__name__}"
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

    if mock:
        logger.info(f"Using mock data set with size {MOCK_SIZE}")

    # Format of MindBigData data set
    columns = [
        "id",
        "event",
        "device",
        "channel",
        "code",
        "size",
        "signal",
    ]
    rows = []

    logger.info("Reading data from %s", in_path)
    with open(in_path, "r") as file:
        for line in file:
            parts = line.strip().split("\t")
            row_dict = {
                "id": int(parts[0]),
                "event": int(parts[1]),
                "device": parts[2],
                "channel": parts[3],
                "code": int(parts[4]),
                "size": int(parts[5]),
                "signal": list(map(float, parts[6].split(","))),
            }
            rows.append(row_dict)
    logger.info("Finished reading data. Applying conversion factor")

    df = pd.DataFrame(rows, columns=columns)
    df.drop(columns=["device"], inplace=True)

    # this corresponds to the LSB of the resolution of the EEG device
    # emotiv.com/products/epoc-x
    conversion_factor = 0.125
    df["signal"] = df["signal"].apply(
        lambda x: np.array(x) * conversion_factor
    )

    if mock:
        df = df.head(MOCK_SIZE)

    df.to_feather(out_path)
    logger.info("Converted file saved to %s", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile",
        type=str,
        help="name of the file to load",
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="name of the file to save the data in feather format",
    )
    parser.add_argument(
        "--mock",
        "-m",
        help="use only a subset of the data",
        action="store_true",
    )

    args = parser.parse_args()
    try:
        main(infile=args.infile, outfile=args.outfile, mock=args.mock)
    except (TypeError, ValueError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
