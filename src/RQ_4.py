"""4. How do the spectrograms of channels F3 and FC6 differ during cognitive tasks, 
and what do these differences reveal about the brain's response in the frontal and frontal-central regions?"""


import mne
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import numpy as np


# Function to plot spectrogram for a given channel
def plot_spectrogram(data, sfreq, channel_name, ax):
    f, t, Sxx = spectrogram(data, fs=sfreq)
    cax = ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
    ax.set_ylabel('Frequency [Hz]')
    ax.set_xlabel('Time [s]')
    ax.set_title(f'Spectrogram for {channel_name}')
    return cax

# Load the epochs data
epochs = mne.read_epochs('../data/denoised_data-epo.fif', preload=True)
sfreq = epochs.info['sfreq']

# Compare spectrograms for two important channels apart from F3 and FC6
important_channels = ["F3", "FC6"]

# Plot spectrograms for the two important channels in one plot
fig, axs = plt.subplots(1, 2, figsize=(20, 6))

for i, channel_name in enumerate(important_channels):
    channel_index = epochs.ch_names.index(channel_name)
    channel_data = epochs.get_data(copy=True)[:, channel_index, :]  # Ensure copy is explicitly set
    flattened_data = channel_data.flatten()
    cax = plot_spectrogram(flattened_data, sfreq, channel_name, axs[i])

fig.colorbar(cax, ax=axs, orientation='vertical', label='Power/Frequency (dB/Hz)')
plt.show()

