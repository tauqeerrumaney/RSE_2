"""
Script for loading and converting EEG data.

This script allows EEG data in a .txt file (in a specific format)
to be loaded, converted into micro Volts based on the input
resolution and saved into a smaller data format.

Usage:
    python3 load_data.py infile outfile [-v]

Positional Arguments:
    infile      Name of the file to load.
    outfile     Name of the file to save the data in feather format.

Optional Arguments:
    -v, --verbose  Use only a subset of the data.

Description:
    The script processes EEG data stored in a .txt file. It expects the file to
    have the following tab-separated columns:
    - id: An integer identifier for the record.
    - event: An integer representing the event code.
    - device: A string identifier for the device.
    - channel: A string representing the EEG channel.
    - code: An integer code for the data type.
    - size: An integer representing the size of the data.
    - signal: A comma-separated list of float values representing EEG signal.

    The script performs the following steps:
    1. Reads the data from the input file.
    2. Converts the signal values from raw units to micro Volts
       using a specified conversion factor.
    3. Optionally saves a subset of the data if the --verbose flag is provided.
    4. Saves processed data into a feather format file for efficient storage.

Modules Required:
    - pandas
    - numpy
    - traceback
    - argparse
    - utils (providing logger and get_path functions)

Functions:
    main(args): Main function to execute the script logic.

Example:
    python script.py input.txt output.feather
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
        args: Command-line arguments parsed by argparse.

    Returns:
        None
    """
    try:
        logger = configure_logger()
        file_path = get_path(infile)
        mock_size = 10000
        if mock:
            logger.info(f"Verbose enabled - {mock_size} rows will be used")
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
    parser = argparse.ArgumentParser(
        description="Script for loading and converting EEG data."
    )
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
