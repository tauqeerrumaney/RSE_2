### Preprocessing Workflow Steps

| Abstract Workflow Node (Operation) | Input(s) | Output(s) | Implementation (Custom Scripts) |
| ------ | ------ | ------ | ------ |
| Data Loading and Filtering | Raw Data Files | filtered_data.csv | Load data and filter using pandas |
| Visual Inspection | filtered_data.csv | inspected_data.csv | Perform automated visual inspection and log results |
| Bandpass Filter | microvolt_data.csv | bandpassed_data.csv | Apply bandpass filter (0.5 - 40 Hz) |
| Artifact Removal (ICA) | bandpassed_data.csv | cleaned_data.csv | Perform ICA to remove artifacts |
| De-Noising (Re-referencing) | cleaned_data.csv | denoised_data.csv | Re-reference signals to reduce noise |
| Feature Extraction | denoised_data.csv | features.csv | Extract features (e.g., power spectral density, wavelet coefficients) |
| Normalization | features.csv | normalized_features.csv | Normalize extracted features |
| Dimensionality Reduction | normalized_features.csv | preprocessed_data.csv | Apply PCA or other dimensionality reduction methods |

### Analysis Workflow Steps

| Abstract Workflow Node (Operation) | Input(s) | Output(s) | Implementation (Custom Scripts) |
| ------ | ------ | ------ | ------ |
| Digit vs Non-Digit Comparison | preprocessed_data.csv | digit_vs_nondigit.csv | Average trials for digit/non-digit, compare differences |
| Low vs High Digit Comparison | preprocessed_data.csv | low_vs_high_digits.csv | Average low (0-4) and high (5-9) digits, compare differences |
| Left vs Right Hemisphere Comparison | preprocessed_data.csv | left_vs_right_hemisphere.csv | Compare differences between left and right hemisphere |
| Frontal vs Parietal Lobe Comparison | preprocessed_data.csv | frontal_vs_parietal_lobe.csv | Compare differences between frontal and parietal lobes |
| Highest Activation Node | preprocessed_data.csv | highest_activation_node.csv | Identify node with highest activation |

### Output Workflow Steps

| Abstract Workflow Node (Operation) | Input(s) | Output(s) | Implementation (Custom Scripts) |
| ------ | ------ | ------ | ------ |
| Visualization Generation | Analysis Data | visualization_plots/ | Generate and save plots using analysis data |
| LaTeX Document Creation | Analysis Data, Visualizations | report.pdf | Write and compile document with conclusions and visualizations |
