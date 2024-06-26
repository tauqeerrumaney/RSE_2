import numpy as np
import pandas as pd
import argparse
from utils import apply_filter_to_signal, logger, set_path


def main(args):
    try:
        # file_name = "raw_data_MOCK.feather"
        file_path = set_path(args.infile)

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

        # output_file_path = set_path("filtered_data.feather")
        output_file_path = set_path(args.outfile)
        df.to_feather(output_file_path)

        print(f"Filtered data saved to {output_file_path}")
        logger.info(f"Filtered data saved to {output_file_path}")

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        print(f"ValueError: {ve}")
    except FileNotFoundError as fnf_error:
        logger.error(f"FileNotFoundError: {fnf_error}")
        print(f"FileNotFoundError: {fnf_error}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    USAGE = "bandpass filter the data"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "--infile",
        "-i",
        type=str,
        help="name of the file to load",
        default="raw_data_MOCK.feather",
    )
    parser.add_argument(
        "--outfile",
        "-o",
        type=str,
        help="name of the file to save the filtered data",
        default="filtered_data.feather",
    )

    args = parser.parse_args()
    main(args)
