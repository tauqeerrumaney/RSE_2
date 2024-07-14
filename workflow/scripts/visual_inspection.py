"""
This script loads EEG data from a feather file, allows filtering by
specific electrode or event, and plots the EEG signal.

Usage:
    Run the script from the command line with the following options:

    ```
    python visual_inspection.py infile [--event EVENT] [--electrode ELECTRODE]
    ```

    Example:
    ```
    python visual_inspection.py filtered_data.feather --event 1
    ```

Options:
    infile (str): Path to the input file containing the EEG data.
    --event (int, optional): Event ID to filter by (set to None to
        plot all data).
    --electrode (str, optional): Electrode to filter by (set to None to
    plot all channels).

Files:
    infile: The input file containing the EEG data in the feather format.

Functions:
    main(infile, event=None, electrode=None):
        Main function to load, filter, and plot EEG data.
"""

import argparse
import os
import traceback

import matplotlib.pyplot as plt
import pandas as pd

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile: str, event: int = None, electrode: str = None):
    """
    Main function to load, filter, and plot EEG data.

    This function loads EEG data from the specified input file, optionally
    filters the data by a specific event ID and/or electrode, and generates
    plots for the filtered data.

    Args:
        infile (str): Path to the input file containing the EEG data.
        event (int, optional): The event ID to filter by. Defaults to None to
            plot all data.
        electrode (str, optional): The electrode to filter by. Defaults to
            None for all data.

    Returns:
        None

    Raises:
        FileNotFoundError: If the input file does not exist.
        TypeError: If the input parameters are not of the expected types.
        ValueError: If the event ID or electrode is not found in the dataframe.
    """
    # Validate input types
    if not isinstance(infile, str):
        raise TypeError(
            f"Expected 'infile' to be of type str, but got "
            f"{type(infile).__name__}"
        )
    if event is not None and not isinstance(event, int):
        raise TypeError(
            f"Expected 'event' to be of type int, but got "
            f"{type(event).__name__}"
        )
    if electrode is not None and not isinstance(electrode, str):
        raise TypeError(
            f"Expected 'electrode' to be of type str, but got "
            f"{type(electrode).__name__}"
        )

    # Validate input file
    in_path = get_path(infile)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    df = pd.read_feather(in_path)
    logger.info("Raw data loaded")

    if electrode is not None:
        # Check if the electrode is within the range of values in the df
        if electrode not in df["channel"].unique():
            raise ValueError(
                f"Electrode {electrode} not found in the dataframe"
            )

        # Filter data for the specified electrode across all events
        electrode_data = df[df["channel"] == electrode]
        logger.info(f"Data for electrode {electrode} loaded")
    else:
        if event is not None:
            # Check if the event_id is within the range of values in the df
            if event not in df["event"].unique():
                raise ValueError(
                    f"Event ID {event} not found in the dataframe"
                )

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
    try:
        main(infile=args.infile, event=args.event, electrode=args.electrode)
    except (TypeError, ValueError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
