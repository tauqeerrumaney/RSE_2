import numpy as np
import pandas as pd
import argparse
from scipy.signal import butter, filtfilt
from utils import apply_filter_to_signal, get_path
from logger import configure_logger

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    y = filtfilt(b, a, data)
    return y


def apply_filter_to_signal(signal, fs, lowcut=0.1, highcut=60.0, order=5):
    return bandpass_filter(signal, lowcut, highcut, fs, order)


def main(args):
    try:
        logger = configure_logger(__name__)
        # file_name = "raw_data_MOCK.feather"
        file_path = get_path(args.infile)

        df = pd.read_feather(file_path)

        logger.info("Raw data loaded")

        if "size" not in df.columns:
            raise ValueError(
                "The DataFrame must contain a 'size' column "
                "representing the sampling rate."
            )

        df["signal"] = df.apply(
            lambda row: apply_filter_to_signal(
                np.array(row["signal"]), row["size"], lowcut=1
            ),
            axis=1,
        )

        output_file_path = get_path(args.outfile)
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
        help="name of the file to load",
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="name of the file to save the filtered data",
    )

    args = parser.parse_args()
    main(args)
