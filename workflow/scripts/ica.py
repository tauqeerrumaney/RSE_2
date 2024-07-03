"""
This script loads EEG data from a feather file, performs
Independent Component Analysis (ICA) to identify and remove artifacts,
and saves the cleaned data to a new file in FIF format.
"""

import argparse
import os
import traceback

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from logger import configure_logger
from mne.preprocessing import ICA
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(infile, outfile, plotfile, artifacts, inspection=False):
    """
    Main function to load, process, and save EEG data using ICA.

    Args:
        infile (str): Name of the file to load.
        outfile (str): Name of the file to save the denoised data.
        artifacts (str): Name of the file containing additional artifact components.
        inspection (bool): Flag to inspect individual components for artifacts.

    Returns:
        None
    """
    try:
        in_path = get_path(infile)

        logger.info("Reading data from %s", in_path)
        df = pd.read_feather(in_path)
        logger.info("Finished reading data. Applying ICA")

        sfreq = df["size"].iloc[0] / 2
        events = df["event"].unique()
        channels = df["channel"].unique()
        target_length = int(2 * sfreq)

        epoch_data = {event: [] for event in events}
        event_codes = {}

        logger.info("Processing data for %d events", len(events))
        for event in events:
            event_df = df[df["event"] == event]
            epoch_signals = []
            for channel in channels:
                channel_signal = event_df[event_df["channel"] == channel][
                    "signal"
                ].values
                if len(channel_signal) > 0:
                    signal = channel_signal[0]
                else:
                    signal = np.zeros(
                        target_length
                    )  # Handle missing channel data by padding with zeros
                epoch_signals.append(signal)
            epoch_data[event] = epoch_signals
            event_codes[event] = event_df["code"].iloc[0]

        epochs_list = [np.array(epoch_data[event]) for event in events]
        epochs_data = np.array(epochs_list)

        # create mne object
        info = mne.create_info(
            ch_names=list(channels),
            sfreq=sfreq,
            ch_types="eeg")

        # set montage, MDB uses 10-20
        montage = mne.channels.make_standard_montage("standard_1020")
        info.set_montage(montage)

        # Create an events array for MNE,
        # each event starts at the next multiple of the epoch length
        event_ids = {
            str(code): idx for idx,
            code in enumerate(
                event_codes.values())}
        events_array = np.array(
            [
                [idx * target_length, 0, event_ids[str(event_codes[event])]]
                for idx, event in enumerate(events)
            ]
        )

        # Check the shape of epochs_data
        logger.info(f"Shape of epochs_data: {epochs_data.shape}")

        # create epochs
        epochs = mne.EpochsArray(
            epochs_data, info, events_array, tmin=0, event_id=event_ids
        )

        ica = ICA(
            n_components=min(
                len(channels),
                20),
            random_state=97,
            max_iter=800)
        ica.fit(epochs)

        # Save the ICA component plots as PNG files - only show them
        # for manual inspection
        png_path = get_path(plotfile)
        fig = ica.plot_components(show=False)
        fig.savefig(png_path)
        plt.close(fig)
        logger.info("ICA component plots saved to %s", png_path)

        # Inspect individual components and
        # get user input for artifacts, if specified
        if inspection:
            identified_artifacts = []
            for i in range(ica.n_components_):
                ica.plot_properties(epochs, picks=[i])
                response = input(f"Mark component {i} as an artifact? (y/n): ")
                if response.lower() == "y":
                    identified_artifacts.append(i)
            logger.info("Identified artifacts: %s", identified_artifacts)
            ica.exclude = identified_artifacts
        elif artifacts is not None:
            additional_artifacts = [int(x) for x in artifacts.split(",")]
            logger.info(
                "Loaded additional artifacts: %s",
                additional_artifacts)
            ica.exclude = additional_artifacts

        # Apply the ICA solution to remove the identified artifacts
        epochs_clean = epochs.copy()
        ica.apply(epochs_clean)

        # Save cleaned epoched data in FIF format for further use with MNE
        out_path = get_path(outfile)
        epochs_clean.save(out_path, overwrite=True)

        logger.info("Cleaned data saved to %s", out_path)

    except FileNotFoundError as e:
        logger.error(f"Could not find file: {e}")
        logger.debug(traceback.format_exc())
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())


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
        help="name of the file to save the denoised data",
    )
    parser.add_argument(
        "plotfile",
        type=str,
        help="name of the file to save the ICA component plots",
    )
    parser.add_argument(
        "--artifacts",
        "-a",
        type=str,
        help="name of config file containing comma-separated artifacts",
        default=None,
    )
    parser.add_argument(
        "--inspect",
        "-i",
        help="inspect individual components for artifacts",
        action="store_true",
    )

    args = parser.parse_args()
    main(
        infile=args.infile,
        outfile=args.outfile,
        plotfile=args.plotfile,
        artifacts=args.artifacts,
        inspection=args.inspect,
    )
