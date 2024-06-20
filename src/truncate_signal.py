import pandas as pd
from utils import logger, set_path

try:
    # Load your dataset
    file_name = "raw_data_MOCK.feather"
    file_path = set_path(file_name)

    df = pd.read_feather(file_path)
    logger.info("Raw data loaded")

    # Determine the minimum size
    target_length = df["size"].min()
    logger.info(f"Minimum size determined: {target_length}")

    # Truncate all signals to the minimum size
    truncated_signals = df["signal"].apply(lambda signal: signal[:target_length])
    df["signal"] = truncated_signals
    logger.info("All signals truncated to the minimum size")

    df["size"] = target_length
    logger.info(f"Size adjusted to {target_length}")
    # Save the truncated data to a new file
    output_file_path = set_path("truncated_data.feather")
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
