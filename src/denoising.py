import mne
import argparse
from utils import logger, get_path


def main(args):

    try:
        input_path = get_path(args.infile)

        epochs = mne.read_epochs(input_path, preload=True)
        logger.info("Artifact filtered data loaded")

        # re-reference to the average of all channels
        epochs.set_eeg_reference("average", projection=True)
        epochs.apply_proj()

        output_path = get_path(args.outfile)

        epochs.save(output_path, overwrite=True)

        logger.info(f"Denoised data saved to {output_path}")
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

    args = parser.parse_args()
    main(args)
