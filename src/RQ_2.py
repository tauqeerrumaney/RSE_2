"""2. How do the EEG signals from channels O1 and O2 differ during various cognitive tasks,
 and what do these differences reveal about lateralized brain activity in the occipital lobe?"""

import mne
import numpy as np
import matplotlib.pyplot as plt

# Load the epochs data
epochs = mne.read_epochs('../data/denoised_data-epo.fif', preload=True)

# Get data for channels O1 and O2
O1_data = epochs.get_data()[:, epochs.ch_names.index('O1'), :]
O2_data = epochs.get_data()[:, epochs.ch_names.index('O2'), :]

# Compute the average across epochs for comparison
O1_avg = np.mean(O1_data, axis=0)
O2_avg = np.mean(O2_data, axis=0)

# Plot the comparison between O1 and O2
plt.figure(figsize=(12, 6))
plt.plot(O1_avg, label='O1')
plt.plot(O2_avg, label='O2')
plt.xlabel('Time (samples)')
plt.ylabel('Amplitude')
plt.title('Comparison of EEG Signals from Channels O1 and O2')
plt.legend()
plt.show()