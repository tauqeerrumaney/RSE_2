"""
Script for applying a bandpass filter to EEG signal data.

This script loads EEG data from a feather file, applies a bandpass filter
to the signals, and saves the filtered data to a new feather file.

Usage:
    python script.py infile outfile

Positional Arguments:
    infile      Name of the file to load.
    outfile     Name of the file to save the filtered data.

Modules Required:
    - numpy
    - pandas
    - argparse
    - scipy.signal (for butter and filtfilt functions)
    - utils (providing apply_filter_to_signal and get_path functions)
    - logger (providing configure_logger function)

Functions:
    bandpass_filter(data, lowcut, highcut, fs, order=5):
        Applies a bandpass filter to the data.
    apply_filter_to_signal(signal, fs, lowcut=0.1, highcut=60.0, order=5):
        Wrapper to apply the bandpass filter.
    main(args): Main function to execute the script logic.

Example:
    python script.py raw_data_MOCK.feather filtered_data.feather
"""

import numpy as np
import pandas as pd
import argparse
from scipy.signal import butter, filtfilt
from utils import get_path
from logger import configure_logger


def bandpass_filter(data, lowcut, highcut, fs, order=5):
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


def apply_filter_to_signal(signal, fs, lowcut=0.1, highcut=60.0, order=5):
    """
    Applies a bandpass filter to the given signal.

    Args:
        signal (array-like): The input signal data to filter.
        fs (float): The sampling frequency of the data.
        lowcut (float, optional): The low cutoff frequency. Default 0.1.
        highcut (float, optional): The high cutoff frequency. Default 60.0.
        order (int, optional): The order of the filter. Default 5.

    Returns:
        array-like: The filtered signal.
    """
    return bandpass_filter(signal, lowcut, highcut, fs, order)


def main(infile, outfile):
    """
    Main function to load, filter, and save EEG signal data.

    This function performs the following steps:
    1. Loads the raw EEG data from the specified input file.
    2. Applies a bandpass filter to each signal in the data.
    3. Saves the filtered data to the specified output file.

    Args:
        infile (str): The path to the input file containing the raw EEG data
        outfile (str): The path to the output file where filtered data is saved

    Returns:
        None
    """
    try:
        logger = configure_logger(__name__)
        file_path = get_path(infile, folder="data")

        df = pd.read_feather(file_path)
        logger.info("Raw data loaded")

        if "size" not in df.columns:
            raise ValueError(
                "DF must contain a 'size' column representing sampling rate."
            )

        df["signal"] = df.apply(
            lambda row: apply_filter_to_signal(
                np.array(row["signal"]), row["size"], lowcut=1
            ),
            axis=1,
        )

        output_file_path = get_path(outfile, folder="data")
        df.to_feather(output_file_path)

        logger.info(f"Filtered data saved to {output_file_path}")

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
        help="name of the file to load"
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="name of the file to save the filtered data"
    )

    args = parser.parse_args()
    main(infile=args.infile, outfile=args.outfile)
