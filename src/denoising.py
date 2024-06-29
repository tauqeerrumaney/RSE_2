import mne
import argparse
from utils import logger, get_path


def main(args):
    # Load the cleaned dataset
    # input_file = "cleaned_data-epo.fif"
    input_path = get_path(args.infile)

    epochs = mne.read_epochs(input_path, preload=True)
    logger.info("Artifact filtered data loaded")

    # re-reference to the average of all channels
    epochs.set_eeg_reference("average", projection=True)
    epochs.apply_proj()

    # output_file = "denoised_data-epo.fif"
    output_path = get_path(args.outfile)

    epochs.save(output_path, overwrite=True)

    logger.info(f"Denoised data saved to {output_path}")
    print(f"Denoised data saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "infile",
        type=str,
        help="name of the file to load",
        # default="cleaned_data-epo.fif",
    )
    parser.add_argument(
        "outfile",
        type=str,
        help="name of the file to save the denoised data",
        # default="denoised_data-epo.fif",
    )

    args = parser.parse_args()
    main(args)
