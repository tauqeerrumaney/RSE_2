"""
This script loads EEG data from a feather file, allows filtering by
specific electrode or event, and plots the EEG signal.
"""

import argparse

import matplotlib.pyplot as plt
import pandas as pd
from logger import configure_logger
from utils import get_path


def main(infile, event, electrode):
    """
    Main function to load, filter, and plot EEG data.

    Args:
        infile (str): The path to the input file containing the EEG data.
        event (int): The event ID to filter by (set to None to plot all data).
        electrode (str): The electrode to filter by (set to None to plot all data).

    Returns:
        None
    """
    logger = configure_logger()
    file_path = get_path(infile)
    df = pd.read_feather(file_path)
    logger.info("Raw data loaded")

    if electrode is not None:
        # Check if the electrode is within the range of values in the df
        if electrode not in df["channel"].unique():
            raise ValueError(f"Electrode {electrode} not found in the dataframe")

        # Filter data for the specified electrode across all events
        electrode_data = df[df["channel"] == electrode]
        logger.info(f"Data for electrode {electrode} loaded")
    else:
        if event is not None:
            # Check if the event_id is within the range of values in the df
            if event not in df["event"].unique():
                raise ValueError(f"Event ID {event} not found in the dataframe")

            # Filter data for the specified event
            electrode_data = df[df["event"] == event]
            logger.info(f"Data for event ID {event} loaded")
        else:
            # Use all data if event_id is None and no electrode specified
            electrode_data = df
            logger.info("All data loaded for plotting")

    # Plot the signals
    plt.figure(figsize=(12, 8))

    if electrode is not None:
        # Plot for the specific electrode across all events
        for idx, row in electrode_data.iterrows():
            plt.plot(
                row["signal"],
                label=f"Electrode {electrode} - Event {row['event']}",
            )
        plt.title(f"EEG Signal for Electrode {electrode} Across All Events")
    else:
        # Plot for all channels for the specified event or all data
        unique_channels = electrode_data["channel"].unique()
        for channel in unique_channels:
            channel_data = electrode_data[electrode_data["channel"] == channel]
            for idx, row in channel_data.iterrows():
                plt.plot(row["signal"], label=f"Channel {channel}")
        if event is not None:
            title = f"EEG Signal for Each Channel (Event {event})"
        else:
            title = "EEG Signal for Each Channel (All Data)"
        plt.title(title)

    plt.xlabel("Sample")
    plt.ylabel("Signal Amplitude (µV)")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("infile", type=str, help="name of the file to load")
    parser.add_argument(
        "--event",
        type=int,
        help="Event to inspect (set to None to plot all data)",
    )
    parser.add_argument(
        "--electrode",
        type=str,
        help="Electrode to inspect (set to None to plot all channels)",
        default=None,
    )

    args = parser.parse_args()
    logger = configure_logger()
    try:
        main(infile=args.infile, event=args.event, electrode=args.electrode)
    except ValueError as ve:
        logger.error(ve)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
