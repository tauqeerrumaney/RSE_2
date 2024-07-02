"""
This script allows EEG data in a .txt file (in a specific format)
to be loaded, converted into micro Volts based on the input
resolution and saved into a smaller data format.
"""

import argparse
import traceback

import numpy as np
import pandas as pd
from logger import configure_logger
from utils import get_path


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
        logger = configure_logger()
        file_path = get_path(infile)
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

        logger.info("Reading data")
        with open(file_path, "r") as file:
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

        df = pd.DataFrame(rows, columns=columns)
        df.drop(columns=["device"], inplace=True)

        # this corresponds to the LSB of the resolution of the EEG device
        # emotiv.com/products/epoc-x
        conversion_factor = 0.125
        df["signal"] = df["signal"].apply(lambda x: np.array(x) * conversion_factor)

        logger.info("Finished reading data")

        try:
            if mock:
                out_path = get_path(f"{outfile}")
                df_mock = df.head(mock_size)
                df_mock.to_feather(out_path)
                logger.info(f"Mock file saved to {out_path}")
            else:
                # save data in feather format -> smaller
                out_path = get_path(f"{outfile}")
                df.to_feather(out_path)
                logger.info(f"Raw file saved to {out_path}")
        # TODO: handle different error types independently
        except Exception:
            logger.error("An error occurred: %s", traceback.format_exc())

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
