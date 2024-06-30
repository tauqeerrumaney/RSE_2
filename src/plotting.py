import mne
from utils import get_path
from logger import configure_logger


try:
    logger = configure_logger(__name__)
    input_file = "denoised_data-epo.fif"  # Path to the denoised file
    input_path = get_path(input_file)

    epochs = mne.read_epochs(input_path, preload=True)

    # Convert epochs to raw for inspection
    raw_data = epochs.get_data()
    info = epochs.info
    n_epochs, n_channels, n_times = raw_data.shape

    raw = mne.io.RawArray(raw_data.reshape(n_channels, -1), info)

    raw.plot(n_channels=len(raw.ch_names), scalings="auto")
    epochs.plot(n_epochs=10, n_channels=10, scalings="auto")
    epochs.plot_psd(fmin=0.1, fmax=60)

    evoked = epochs.average()
    evoked.plot()

except ValueError as ve:
    logger.error(f"ValueError: {ve}")
except FileNotFoundError as fnf_error:
    logger.error(f"FileNotFoundError: {fnf_error}")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")
