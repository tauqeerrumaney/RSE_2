### Preprocessing Workflow Steps

| Abstract Workflow Node (Operation) | Input(s) | Output(s) | Implementation (Custom Scripts) |
| ------ | ------ | ------ | ------ |
| Data Loading and Filtering | Raw Data Files | filtered_data.feather | Load data and filter |
| Bandpass Filter | filtered_data.feather | bandpassed_data.feather | Apply bandpass filter (1 - 60 Hz) |
| Truncate Data | bandpassed_data.feather | truncated_data.feather | Truncate data to desired time window |
| Artifact Removal (ICA) | truncated_data.feather | cleaned_epo.fif, ica_components.png | Perform ICA to remove artifacts |
| De-Noising (Re-referencing) | cleaned_epo.fif | denoised_epo.fif | Re-reference signals to reduce noise |
| Feature Extraction | denoised_epo.fif | features.npy | Extract features (e.g., power spectral density, wavelet coefficients) |

### Analysis Workflow Steps

| Abstract Workflow Node (Operation) | Input(s) | Output(s) | Implementation (Custom Scripts) |
| ------ | ------ | ------ | ------ |
| Research Question 1 | denoised_epo.fif | rq_1.png, rq_1.json | Which frequency bands show the highest variability across different events, indicating event-related changes in brain activity? |
| Research Question 2 | denoised_epo.fif | rq_2.png | How do the EEG signals from channels O1 and O2 differ during various cognitive tasks, and what do these differences reveal about lateralized brain activity in the occipital lobe?|
| Research Question 3 | denoised_epo.fif | rq_3.png | How does the event-related potential (ERP) differ across channels such as AF3 (frontal), P7 (parietal), and O1 (occipital) for a specific cognitive task in the EPOC data? |
| Research Question 4 | denoised_epo.fif | rq_4.png | How do the spectrograms of channels F3 and FC6 differ during cognitive tasks, and what do these differences reveal about the brain's response in the frontal and frontal-central regions?|
| Research Question 5 | features.npy | rq_5.png | How do the kurtosis values of EEG signals vary across different epochs for channels FC6, F4, and F8, and what do these variations reveal about the underlying neural dynamics? |

### Output Workflow Steps

| Abstract Workflow Node (Operation) | Input(s) | Output(s) | Implementation (Custom Scripts) |
| ------ | ------ | ------ | ------ |
| Generate Plots | denoised_epo.fif | denoised_epo_epochs.png, denoised_epo_psd.png, denoised_epo_response.png, denoised_epo_raw.png | Generate and save plots using epo data |
| LaTeX Document Creation | Analysis Data | report.pdf | Write and compile document with conclusions and visualizations |
