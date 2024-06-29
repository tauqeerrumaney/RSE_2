import pandas as pd
import argparse
from utils import logger, get_path


def main(args):
    try:
        # file_name = "filtered_data.feather"
        file_path = get_path(args.infile)

        df = pd.read_feather(file_path)
        logger.info("Bandpass filtered data loaded")

        target_length = min(df["size"])

        # Truncate all signals to the target length
        truncated_signals = df["signal"].apply(
            lambda signal: signal[:target_length]
        )
        df["signal"] = truncated_signals
        logger.info("All signals truncated to the target length")

        # Validate that all signals are of length 248
        # -> can also be implemented in a test file
        if not all(df["signal"].apply(len) == target_length):
            raise ValueError("Not all signals are of length 248")

        df["size"] = target_length
        logger.info(f"Size adjusted to {target_length}")

        # output_file = "truncated_data.feather"
        output_file_path = get_path(args.outfile)
        df.to_feather(output_file_path)

        print(f"Truncated data saved to {output_file_path}")
        logger.info(f"Truncated data saved to {output_file_path}")

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
    # USAGE = "truncating the signals to the target length"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile",
        type=str,
        help="name of the file to load",
        # default="filtered_data.feather",
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="name of the file to load",
        # default="truncated_data.feather",
    )

    args = parser.parse_args()
    main(args)
