import mne
import argparse
from utils import logger, set_path


def main(args):
    # Load the cleaned dataset
    # input_file = "cleaned_data-epo.fif"
    input_path = set_path(args.infile)

    epochs = mne.read_epochs(input_path, preload=True)
    logger.info("Artifact filtered data loaded")

    # re-reference to the average of all channels
    epochs.set_eeg_reference("average", projection=True)
    epochs.apply_proj()

    output_file = "denoised_data-epo.fif"
    output_path = set_path(output_file)

    epochs.save(output_path, overwrite=True)

    logger.info(f"Denoised data saved to {output_path}")
    print(f"Denoised data saved to {output_path}")


if __name__ == "__main__":
    USAGE = "Denoise the data"
    parser = argparse.ArgumentParser(description=USAGE)
    parser.add_argument(
        "--infile",
        "-i",
        type=str,
        help="name of the file to load",
        default="cleaned_data-epo.fif",
    )

    args = parser.parse_args()
    main(args)
