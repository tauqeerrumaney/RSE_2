import logging
import os
from scipy.signal import butter, filtfilt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# TODO change to actual filename
logger = logging.getLogger(__name__)


def get_path(file_name):
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, f"../data/{file_name}")
    return file_path


def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    y = filtfilt(b, a, data)
    return y


def apply_filter_to_signal(signal, fs, lowcut=0.1, highcut=60.0, order=5):
    return bandpass_filter(signal, lowcut, highcut, fs, order)
