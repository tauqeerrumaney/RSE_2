"""
This script loads EEG data from a feather file, applies a bandpass filter
to the signals, and saves the filtered data to a new feather file.
"""

import argparse

import numpy as np
import pandas as pd
from logger import configure_logger
from scipy.signal import butter, filtfilt
from utils import get_path


def bandpass_filter(data, fs, lowcut=0.1, highcut=60.0, order=5):
    """
    Applies a bandpass filter to the given data.

    Args:
        data (array-like): The input signal data to filter.
        lowcut (float): The low cutoff frequency of the filter.
        highcut (float): The high cutoff frequency of the filter.
        fs (float): The sampling frequency of the data.
        order (int, optional): The order of the filter. Default is 5.

    Returns:
        array-like: The filtered signal.
    """
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    y = filtfilt(b, a, data)
    return y


def main(infile, outfile):
    """
    Main function to load, filter, and save EEG signal data.

    Args:
        infile (str): The path to the input file containing the raw EEG data.
        outfile (str): The path to the output file where filtered data is saved.

    Returns:
        None
    """
    logger = configure_logger()
    file_path = get_path(infile)

    df = pd.read_feather(file_path)
    logger.info("Raw data loaded")

    if "size" not in df.columns:
        raise ValueError("DF must contain a 'size' column representing sampling rate.")

    df["signal"] = df.apply(
        lambda row: bandpass_filter(np.array(row["signal"]), row["size"], lowcut=1),
        axis=1,
    )

    output_file_path = get_path(outfile)
    df.to_feather(output_file_path)

    logger.info(f"Filtered data saved to {output_file_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "outfile", type=str, help="name of the file to save the filtered data"
    )
    logger = configure_logger()
    args = parser.parse_args()

    try:
        main(infile=args.infile, outfile=args.outfile)
    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
