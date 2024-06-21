import pandas as pd
import numpy as np
import mne
from mne.preprocessing import ICA
from utils import logger, set_path

INSPEC = False

file_name = "truncated_data.feather"
file_path = set_path(file_name)

df = pd.read_feather(file_path)
logger.info("MindBigData EPOC data loaded")


sfreq = df['size'].iloc[0] / 2  
events = df['event'].unique()
channels = df['channel'].unique()
# target length is 2 time the sampling frequency
target_length = int(2 * sfreq)

epoch_data = {event: [] for event in events}
event_codes = {}

for event in events:
    event_df = df[df['event'] == event]
    epoch_signals = []
    for channel in channels:
        channel_signal = event_df[event_df['channel'] == channel]['signal'].values
        if len(channel_signal) > 0:
            signal = channel_signal[0]

        else:
            signal = np.zeros(target_length)  # Handle missing channel data by padding with zeros
        epoch_signals.append(signal)
    epoch_data[event] = epoch_signals
    event_codes[event] = event_df['code'].iloc[0]

epochs_list = [np.array(epoch_data[event]) for event in events]
epochs_data = np.array(epochs_list)

# create mne object
info = mne.create_info(ch_names=list(channels), sfreq=sfreq, ch_types='eeg')

# set montage, MDB uses 10-20
montage = mne.channels.make_standard_montage('standard_1020')
info.set_montage(montage)

# Create an events array for MNE, each event starts at the next multiple of the epoch length
event_ids = {str(code): idx for idx, code in enumerate(event_codes.values())}
events_array = np.array([[idx * target_length, 0, event_ids[str(event_codes[event])]] for idx, event in enumerate(events)])

# Check the shape of epochs_data
logger.info(f"Shape of epochs_data: {epochs_data.shape}")

# create epochs
epochs = mne.EpochsArray(epochs_data, info, events_array, tmin=0, event_id=event_ids)
print(epochs)
ica = ICA(n_components=min(len(channels), 20), random_state=97, max_iter=800)
ica.fit(epochs)
ica.plot_components()

#Inspect individual components and get user input for artifacts, if specified
identified_artifacts = []

if INSPEC:
    for i in range(ica.n_components_):
        ica.plot_properties(epochs, picks=[i])
        response = input(f"Mark component {i} as an artifact? (y/n): ")
        if response.lower() == 'y':
            identified_artifacts.append(i)
else:
    additional_artifacts = input("Enter suspected artifact components (comma-separated): ")
    if additional_artifacts:
        additional_artifacts = list(map(int, additional_artifacts.split(',')))
    else:
        additional_artifacts = []

logger.info(f"Identified artifact components: {identified_artifacts}")
ica.exclude = identified_artifacts
# Apply the ICA solution to remove the identified artifacts
epochs_clean = epochs.copy()
ica.apply(epochs_clean)

# svae cleaned epoched data in fif format for further use with mne
output_path = set_path("cleaned_data-epo.fif")
epochs_clean.save(output_path, overwrite=True)

logger.info(f"Cleaned data saved to {output_path}")

