"""
Script for performing ICA on EEG data and removing artifacts.

This script loads EEG data from a feather file, performs
Independent Component Analysis (ICA) to identify and remove artifacts,
and saves the cleaned data to a new file in FIF format.

Usage:
    python script.py infile outfile [--verbose] [--artifacts artifact_list]

Positional Arguments:
    infile      Name of the file to load.
    outfile     Name of the file to save the denoised data.

Optional Arguments:
    --verbose, -v           Inspect individual components for artifacts interactively.
    --artifacts, -a         Comma-separated list of artifact components.

Modules Required:
    - pandas
    - numpy
    - mne
    - argparse
    - mne.preprocessing (for ICA)
    - utils (providing get_path function)
    - logger (providing configure_logger function)

Functions:
    main(infile, outfile, artifacts=None, verbose=False): Main function to execute the script logic.

Example:
    python script.py truncated_data.feather cleaned_data.fif --verbose -a config/artifacts.txt
"""

import pandas as pd
import numpy as np
import mne
import argparse
import matplotlib.pyplot as plt
from mne.preprocessing import ICA
from utils import get_path
from logger import configure_logger
from pathlib import Path


def main(infile, outfile, artifacts=None, inspection=False):
    """
    Main function to load, process, and save EEG data using ICA.

    This function performs the following steps:
    1. Loads the truncated EEG data from the specified input file.
    2. Organizes the data into epochs and creates an MNE Epochs object.
    3. Fits an ICA model to the data to identify artifacts.
    4. Optionally inspects individual components for artifacts interactively.
    5. Removes identified artifact components from the data.
    6. Saves the cleaned data to the specified output file in FIF format.

    Args:
        infile (str): Name of the file to load.
        outfile (str): Name of the file to save the denoised data.
        artifacts (str, optional): Comma-separated list of artifact components. Defaults to None.
        verbose (bool, optional): If True, inspect individual components for artifacts interactively. Defaults to False.

    Returns:
        None
    """
    try:
        logger = configure_logger()
        file_path = get_path(infile)

        df = pd.read_feather(file_path)
        logger.info("Truncated data loaded")

        sfreq = df["size"].iloc[0] / 2
        events = df["event"].unique()
        channels = df["channel"].unique()
        target_length = int(2 * sfreq)

        epoch_data = {event: [] for event in events}
        event_codes = {}

        for event in events:
            event_df = df[df["event"] == event]
            epoch_signals = []
            for channel in channels:
                channel_signal = event_df[event_df["channel"] == channel]["signal"].values
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
        info = mne.create_info(ch_names=list(channels), sfreq=sfreq, ch_types="eeg")

        # set montage, MDB uses 10-20
        montage = mne.channels.make_standard_montage("standard_1020")
        info.set_montage(montage)

        # Create an events array for MNE,
        # each event starts at the next multiple of the epoch length
        event_ids = {str(code): idx for idx, code in enumerate(event_codes.values())}
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

        ica = ICA(n_components=min(len(channels), 20), random_state=97, max_iter=800)
        ica.fit(epochs)
        # Save the ICA component plots as PNG files - only show them
        # for manual inspection
        png_path = get_path("results/ica_components.png")
        fig = ica.plot_components(show=False)
        fig.savefig(png_path)
        plt.close(fig)

        # Inspect individual components and
        # get user input for artifacts, if specified
        identified_artifacts = []

        if inspection:
            for i in range(ica.n_components_):
                ica.plot_properties(epochs, picks=[i])
                response = input(f"Mark component {i} as an artifact? (y/n): ")
                if response.lower() == "y":
                    identified_artifacts.append(i)
        elif artifacts is not None:
            with open(get_path(artifacts), "r") as file:
                contents = file.read()
            additional_artifacts = [int(x) for x in contents.split(",")]
        else:
            artifact_path = Path(get_path("config/artifacts.txt"))
            artifact_path.touch(exist_ok=True)
        logger.info(f"Identified artifact components: {additional_artifacts}")
        ica.exclude = additional_artifacts

        # Apply the ICA solution to remove the identified artifacts
        epochs_clean = epochs.copy()
        ica.apply(epochs_clean)

        # Save cleaned epoched data in FIF format for further use with MNE
        output_path = outfile
        epochs_clean.save(output_path, overwrite=True)

        logger.info(f"Cleaned data saved to {output_path}")

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
        help="name of the file to save the denoised data",
    )
    parser.add_argument(
        "--artifacts",
        "-a",
        type=str,
        help="name of config file containing comma-separated artifacts",
        default="",
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
        artifacts=args.artifacts,
        verbose=args.inspect,
    )
