"""3. How does the event-related potential (ERP) differ across channels such as AF3 (frontal), P7 (parietal), 
and O1 (occipital) for a specific cognitive task in the EPOC data?"""

import mne
import numpy as np
import matplotlib.pyplot as plt

# Load the epochs data
epochs = mne.read_epochs('../data/denoised_data-epo.fif', preload=True)

# Get unique event types
event_ids = np.unique(epochs.events[:, 2])

# Function to plot ERP for a given event type and channels
def plot_erp_for_event(epochs, event_id, channels):
    plt.figure(figsize=(12, 8))
    erp = epochs[event_id].average()
    for channel in channels:
        plt.plot(erp.times, erp.data[erp.ch_names.index(channel)], label=f'{channel}')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (µV)')
    plt.title(f'ERP for Event {event_id} at Selected Channels')
    plt.legend()
    plt.show()

# Select a single event type for comparison
event_id = event_ids[0]

# Select a few important channels for comparison
important_channels = ["AF3", "P7", "O1"]

# Plot ERP for the selected event type and channels
plot_erp_for_event(epochs, event_id, important_channels)
