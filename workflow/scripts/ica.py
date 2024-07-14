"""
This script loads EEG data from a feather file, performs Independent
Component Analysis (ICA) to identify and remove artifacts, and saves the
cleaned data to a new file in FIF format.

Usage:
    Run the script from the command line with the following options:

    ```
    python ica.py infile outfile plotfile [--artifacts ARTIFACTS] [--inspect]
    ```

    Example:
    ```
    python ica.py truncated_data.feather cleaned_epo.fif ica_components.png
    --artifacts 1,2,3 --inspect
    ```

Options:
    infile (str): Path to the input file contains truncated data.
    outfile (str): Path to save the cleaned data.
    plotfile (str): Path to save the ICA component plots.
    --artifacts (str, optional): Comma-separated list of integer artifacts
        to remove. Default is None.
    --inspect (bool, optional): Flag to inspect individual components for
        artifacts. Default is False.

Files:
    infile: The input file contains truncated data in the feather format.
    outfile: The output file where the cleaned EEG data will be saved in
        FIF format.
    plotfile: The output file where the ICA component plots will be saved
        in png format.

Functions:
    main(infile, outfile, plotfile, artifacts, inspection):
        Main function to load, process, and save EEG data using ICA.
"""

import argparse
import os
import traceback

import matplotlib.pyplot as plt
import mne
import numpy as np
import pandas as pd
from mne.preprocessing import ICA

from logger import configure_logger
from utils import get_path

logger = configure_logger(os.path.basename(__file__))


def main(
    infile: str, outfile: str, plotfile: str, artifacts: str, inspection: bool
):
    """
    Load, process, and save EEG data using ICA.

    This function reads EEG data from a feather file, performs ICA to identify
    and remove artifacts, and saves the cleaned data to a new file
    in FIF format. Optionally, it can save plots of the ICA components
    and allow inspection of individual components for artifact identification.

    Args:
        infile (str): Path to the input file contains trruncated data.
        outfile (str): Path to the output file where the cleaned data saved.
        plotfile (str): Path to save the ICA component plots.
        artifacts (str, optional): Comma-separated list of integer artifacts
            to remove. Default is None.
        inspection (bool, optional): Flag to inspect individual components for
            artifacts. Default is False.

    Returns:
        None

    Raises:
        FileNotFoundError: If the input file does not exist.
        TypeError: If the input parameters are not of the expected types.
        ValueError: If the output directory does not exist or if the artifacts
            list is not a comma-separated list of integers.
    """
    # Validate input types
    if not isinstance(infile, str):
        raise TypeError(
            f"Expected 'infile' to be of type str, but got "
            f"{type(infile).__name__}"
        )
    if not isinstance(outfile, str):
        raise TypeError(
            f"Expected 'outfile' to be of type str, but got "
            f"{type(outfile).__name__}"
        )
    if not isinstance(plotfile, str):
        raise TypeError(
            f"Expected 'plotfile' to be of type str, but got "
            f"{type(plotfile).__name__}"
        )
    if artifacts is not None and not isinstance(artifacts, str):
        raise TypeError(
            f"Expected 'artifacts' to be of type str, but got "
            f"{type(artifacts).__name__}"
        )
    if artifacts is not None and not all(
        x.isdigit() for x in artifacts.split(",")
    ):
        raise ValueError(
            "Artifacts must be a comma-separated list of integers"
        )
    if not isinstance(inspection, bool):
        raise TypeError(
            f"Expected 'inspection' to be of type bool, but got "
            f"{type(inspection).__name__}"
        )

    # Validate input file
    in_path = get_path(infile)
    if not os.path.exists(in_path):
        raise FileNotFoundError(f"Input file not found: {in_path}")

    # Validate output file
    out_path = get_path(outfile)
    out_dir = os.path.dirname(out_path)
    if not os.path.exists(out_dir):
        raise ValueError(f"Output directory does not exist: {out_dir}")

    plot_path = get_path(plotfile)
    plot_dir = os.path.dirname(plot_path)
    if not os.path.exists(plot_dir):
        raise ValueError(f"Output directory does not exist: {plot_dir}")

    # Load the data from the input file
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
        ch_names=list(channels), sfreq=sfreq, ch_types="eeg"
    )

    # set montage, MDB uses 10-20
    montage = mne.channels.make_standard_montage("standard_1020")
    info.set_montage(montage)

    # Create an events array for MNE,
    # each event starts at the next multiple of the epoch length
    event_ids = {
        str(code): idx for idx, code in enumerate(event_codes.values())
    }
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
        n_components=min(len(channels), 20), random_state=97, max_iter=800
    )
    ica.fit(epochs)

    # Save the ICA component plots as PNG files - only show them
    # for manual inspection
    fig = ica.plot_components(show=False)
    fig.savefig(plot_path)
    plt.close(fig)
    logger.info("ICA component plots saved to %s", plot_path)

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
        logger.info("Loaded additional artifacts: %s", additional_artifacts)
        ica.exclude = additional_artifacts

    # Apply the ICA solution to remove the identified artifacts
    epochs_clean = epochs.copy()
    ica.apply(epochs_clean)

    # Save cleaned epoched data in FIF format for further use with MNE
    epochs_clean.save(out_path, overwrite=True)
    logger.info("Cleaned data saved to %s", out_path)


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
    try:
        main(
            infile=args.infile,
            outfile=args.outfile,
            plotfile=args.plotfile,
            artifacts=args.artifacts,
            inspection=args.inspect,
        )
    except (TypeError, ValueError, FileNotFoundError) as e:
        logger.error(e)
        logger.debug(traceback.format_exc())
        exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
        logger.debug(traceback.format_exc())
        exit(99)
