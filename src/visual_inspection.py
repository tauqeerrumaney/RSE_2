from utils import logger
import pandas as pd
import matplotlib.pyplot as plt
import os

# File loading
file_name = "raw_data_MOCK.feather"
# Event to inspect (set to None to plot all data)
# from 67635 to 68349 -> 714 unique events
event_id = 67637
# Electrode to inspect (set to None to plot all channels)
electrode = None

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, f"../data/{file_name}")

df = pd.read_feather(file_path)
logger.info("Raw data loaded")

# min_event_id = df["event"].min()
# max_event_id = df["event"].max()
# print(max_event_id - min_event_id)

try:
    if electrode is not None:
        # Check if the electrode is within the range of values in the dataframe
        if electrode not in df["channel"].unique():
            raise ValueError(f"Electrode {electrode} not found in the dataframe")

        # Filter data for the specified electrode across all events
        electrode_data = df[df["channel"] == electrode]
        logger.info(f"Data for electrode {electrode} loaded")
    else:
        if event_id is not None:
            # Check if the event_id is within the range of values in the dataframe
            if event_id not in df["event"].unique():
                raise ValueError(f"Event ID {event_id} not found in the dataframe")

            # Filter data for the specified event
            electrode_data = df[df["event"] == event_id]
            logger.info(f"Data for event ID {event_id} loaded")
        else:
            # Use all data if event_id is None and no electrode is specified
            electrode_data = df
            logger.info("All data loaded for plotting")

    # Plot the signals
    plt.figure(figsize=(12, 8))

    if electrode is not None:
        # Plot for the specific electrode across all events
        for idx, row in electrode_data.iterrows():
            plt.plot(
                row["signal"], label=f"Electrode {electrode} - Event {row['event']}"
            )
        plt.title(f"EEG Signal for Electrode {electrode} Across All Events")
    else:
        # Plot for all channels for the specified event or all data
        unique_channels = electrode_data["channel"].unique()
        for channel in unique_channels:
            channel_data = electrode_data[electrode_data["channel"] == channel]
            for idx, row in channel_data.iterrows():
                plt.plot(row["signal"], label=f"Channel {channel}")
        title = (
            f"EEG Signal for Each Channel (Event {event_id})"
            if event_id is not None
            else "EEG Signal for Each Channel (All Data)"
        )
        plt.title(title)

    plt.xlabel("Sample")
    plt.ylabel("Signal Amplitude (µV)")
    plt.legend()
    plt.show()

except ValueError as ve:
    logger.error(ve)
    print(ve)
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
    print(f"An unexpected error occurred: {e}")
