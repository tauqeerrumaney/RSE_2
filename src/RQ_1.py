""" Question 1: Which frequency bands show the highest variability across different events, 
indicating event-related changes in brain activity?"""

import mne
import numpy as np
import pandas as pd
from scipy.signal import welch
import matplotlib.pyplot as plt

# Load the epochs data
epochs = mne.read_epochs('../data/denoised_data-epo.fif', preload=True)
sfreq = epochs.info['sfreq']

# Define frequency bands
bands = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 45),
}

def compute_psd(data, sfreq, band):
    # Compute the PSD using Welch's method
    freqs, psd = welch(data, sfreq, nperseg=248)
    band_freqs = (freqs >= band[0]) & (freqs <= band[1])
    return np.mean(psd[:, band_freqs], axis=1)

# Calculate PSD for each band and event
psd_values = {band: [] for band in bands}
for event_id in range(len(epochs.events)):
    epoch_data = epochs[event_id].get_data(copy=True)  
    for band, freq_range in bands.items():
        psd_band_values = []
        for channel_data in epoch_data:
            psd_band_values.append(compute_psd(channel_data, sfreq, freq_range))
        psd_values[band].append(np.array(psd_band_values).mean(axis=0))

# Convert to DataFrame for easier analysis
psd_df = {band: pd.DataFrame(psd_values[band]) for band in psd_values.keys()}

# Calculate variability (standard deviation) across events
variability = {band: psd_df[band].std(axis=1) for band in psd_df.keys()}

# Identify bands with highest variability
highest_variability = max(variability, key=lambda band: variability[band].mean())
print(f"The frequency band with the highest variability is: {highest_variability}")

# Display variability for each band
for band, var in variability.items():
    print(f"Variability in {band} band: {var.mean()}")

# Extracting bands and their corresponding variability values
bands = list(variability.keys())
variability_values = [var.mean() for var in variability.values()]

# Plotting the variability for each frequency band
plt.figure(figsize=(10, 6))
plt.bar(bands, variability_values, color='skyblue')
plt.xlabel('Frequency Band')
plt.ylabel('Variability (Standard Deviation)')
plt.title('Variability in Frequency Bands Across Different Events')
plt.show()
