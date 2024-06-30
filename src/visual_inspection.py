"""
Script for loading, filtering, and plotting EEG data.

This script loads EEG data from a feather file, allows filtering by
specific electrode or event, and plots the EEG signal.

Usage:
    python script.py infile [--event EVENT] [--electrode ELECTRODE]

Positional Arguments:
    infile          Name of the file to load.

Optional Arguments:
    --event         Event to inspect (set to None to plot all data).
    --electrode     Electrode to inspect (set to None to plot all channels).

Description:
    The script performs the following steps:
    1. Loads the EEG data from the specified input file.
    2. Filters the data based on the specified electrode or event.
    3. Plots the EEG signal for all data or filtered data if specified.

Modules Required:
    - pandas
    - matplotlib.pyplot
    - argparse
    - utils (providing logger and get_path functions)

Functions:
    main(args): Main function to execute the script logic.

Example:
    python script.py data.feather --event 1 --electrode Fz
"""

from utils import logger, get_path
import pandas as pd
import matplotlib.pyplot as plt
import argparse


def main(args):
    """
    Main function to load, filter, and plot EEG data.

    Args:
        args: Command-line arguments parsed by argparse.

    Returns:
        None
    """
    file_path = get_path(args.infile)
    event = args.event
    df = pd.read_feather(file_path)
    logger.info("Raw data loaded")

    try:
        if args.electrode is not None:
            # Check if the electrode is within the range of values in the df
            if args.electrode not in df["channel"].unique():
                raise ValueError(
                    f"Electrode {args.electrode} not found in the dataframe"
                )

            # Filter data for the specified electrode across all events
            electrode_data = df[df["channel"] == args.electrode]
            logger.info(f"Data for electrode {args.electrode} loaded")
        else:
            if args.event is not None:
                # Check if the event_id is within the range of values in the df
                if args.event not in df["event"].unique():
                    raise ValueError(
                        f"Event ID {args.event} not found in the dataframe"
                    )

                # Filter data for the specified event
                electrode_data = df[df["event"] == args.event]
                logger.info(f"Data for event ID {args.event} loaded")
            else:
                # Use all data if event_id is None and no electrode specified
                electrode_data = df
                logger.info("All data loaded for plotting")

        # Plot the signals
        plt.figure(figsize=(12, 8))

        if args.electrode is not None:
            # Plot for the specific electrode across all events
            for idx, row in electrode_data.iterrows():
                plt.plot(
                    row["signal"],
                    label=f"Electrode {args.electrode} - Event {row['event']}",
                )
            plt.title(
                f"EEG Signal for Electrode {args.electrode} Across All Events"
            )
        else:
            # Plot for all channels for the specified event or all data
            unique_channels = electrode_data["channel"].unique()
            for channel in unique_channels:
                channel_data = electrode_data[
                    electrode_data["channel"] == channel
                ]
                for idx, row in channel_data.iterrows():
                    plt.plot(row["signal"], label=f"Channel {channel}")
            title = (
                f"EEG Signal for Each Channel (Event {event})"
                if event is not None
                else "EEG Signal for Each Channel (All Data)"
            )
            plt.title(title)

        plt.xlabel("Sample")
        plt.ylabel("Signal Amplitude (µV)")
        plt.legend()
        plt.show()

    except ValueError as ve:
        logger.error(ve)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


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
    main(args)
