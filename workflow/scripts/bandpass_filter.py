"""
This script loads EEG data from a feather file, applies a bandpass filter
to the signals, and saves the filtered data to a new feather file.

Usage:
    Run the script from the command line with the following options:

    ```
    python bandpass_filter.py infile outfile
    ```

    Example:
    ```
    python bandpass_filter.py filtered_data.feather bandpassed_data.feather
    ```

Options:
    infile (str): Path to the input file containing the converted data.
    outfile (str): Path to the output file where the data is saved.

Files:
    infile: The input file contains the filtered data in the feather format.
    outfile: The output file where the bandpass filter will be saved in
        feather format.

Functions:
    main(infile, outfile):
        Loads, filters, and saves EEG signal data.
    bandpass_filter(data, fs, lowcut=1.0, highcut=40.0, order=5):
        Applies a bandpass filter to the given data.
"""

import argparse
import os
import traceback

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def bandpass_filter(data, fs, lowcut=1.0, highcut=60.0, order=5):
    """
    Applies a bandpass filter to the given data.

    This function applies a Butterworth bandpass filter to the input data.
    The bandpass filter allows frequencies within a specified range to
    pass through while attenuating frequencies outside that range.

    Args:
        data (array-like): The input signal data to filter.
        fs (float): The sampling frequency of the data.
        lowcut (float): The low cutoff frequency of the filter.
        highcut (float): The high cutoff frequency of the filter.
        order (int, optional): The order of the filter. Default is 5.

    Returns:
        array-like: The filtered signal.

    Raises:
        ValueError: If the lowcut or highcut frequencies are not
        within the valid range.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    y = filtfilt(b, a, data)
    return y


def main(infile: str, outfile: str):
    """
    load, filter, and save EEG signal data.

    This function reads EEG signal data from the specified input file,
    applies a bandpass filter to the data, and saves the filtered data
    to the specified output file.

    Args:
        infile (str): Path to the input file containing the converted data.
        outfile (str): Path to the file where output data will be saved.

    Returns:
        None

    Raises:
        FileNotFoundError: If the input file does not exist.
        TypeError: If the input parameters are not of the expected types.
        ValueError: If the DataFrame does not contain a 'size' column.
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

    # Read the data from the input file
    logger.info("Reading data from %s", in_path)
    df = pd.read_feather(in_path)
    logger.info("Finished reading data. Applying bandpass filter")

    if "size" not in df.columns:
        raise ValueError(
            "DF must contain a 'size' column representing sampling rate."
        )

    df["signal"] = df.apply(
        lambda row: bandpass_filter(np.array(row["signal"]), row["size"]),
        axis=1,
    )

    out_path = get_path(outfile)
    df.to_feather(out_path)
    logger.info("Bandpassed data saved to %s", out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "outfile", type=str, help="name of the file to save the filtered data"
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
