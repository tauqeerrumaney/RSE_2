"""5. How do the kurtosis values of EEG signals vary across different epochs for channels FC6, F4, and F8, 
and what do these variations reveal about the underlying neural dynamics?"""

import numpy as np
import matplotlib.pyplot as plt

# Load the extracted features
features = np.load('../data/extracted_features.npy', allow_pickle=True).item()

# Plotting kurtosis values for selected channels
channels = ['FC6', 'F4', 'F8']
plt.figure(figsize=(10, 6))
for channel in channels:
    key = f"{channel}_kurtosis"
    if key in features:
        plt.plot(features[key], label=channel)
plt.title('Kurtosis Values')
plt.xlabel('Epochs')
plt.ylabel('Kurtosis')
plt.legend()
plt.tight_layout()
plt.show()
