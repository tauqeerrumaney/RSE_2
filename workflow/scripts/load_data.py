"""
This script allows EEG data in a .csv file (in a specific format)
to be loaded, converted into micro Volts based on the input
resolution and saved into a smaller data format.
"""

import argparse
import os
import traceback

import numpy as np
import pandas as pd
from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))

def main(infile, outfile, mock=False):
    """
    Main function to load, process, and save EEG data.

    Args:
        infile (str): The path to the input file containing the raw EEG data.
        outfile (str): The path to the output file where the data is saved.
        mock (bool): Whether to use a subset of the data for testing purposes.

    Returns:
        None
    """
    try:
        in_path = get_path(infile)

        mock_size = 10000
        if mock:
            logger.info(f"Using mock data set with size {mock_size}")

        # format of MindBigData data set
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
            lambda x: np.array(x) * conversion_factor)

        # save the data in feather format
        out_path = get_path(outfile)
        if mock:
            df = df.head(mock_size)
        df.to_feather(out_path)

        logger.info("Converted file saved to %s", out_path)

    except FileNotFoundError as e:
        logger.error(f"Could not find file: {e}")
        logger.debug(traceback.format_exc())
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())


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
    main(infile=args.infile, outfile=args.outfile, mock=args.mock)
