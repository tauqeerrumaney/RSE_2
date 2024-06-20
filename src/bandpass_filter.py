import numpy as np
import pandas as pd
import os
from utils import apply_filter_to_signal, logger, set_path

try:
    file_name = "raw_data_MOCK.feather"
    file_path = set_path(file_name)

    df = pd.read_feather(file_path)
    logger.info("Raw data loaded")

    # Ensure there's a column 'size' indicating the sampling rate for each event
    if 'size' not in df.columns:
        raise ValueError("The DataFrame must contain a 'size' column representing the sampling rate.")

    # Apply the filter to each signal in the dataframe using its corresponding sampling rate
    df['filtered_signal'] = df.apply(
        lambda row: apply_filter_to_signal(np.array(row['signal']), row['size']), axis=1
    )

    # Save the filtered data to a new file
    output_file_path = set_path("filtered_data.feather")
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
