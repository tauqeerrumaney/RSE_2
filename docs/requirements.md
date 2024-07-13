## Requirement Definition
This document outlines the functional and non-functional requirements for the project. The goal is to provide a detailed specification that ensures the workflow meets the necessary criteria for data management, analytical processing, data transformation, result generation, and automation.

### Functional Requirements

### User-Stories:

**Must have:**

"As a researcher, I want to be able to preprocess my EEG data using a defined sequence of steps."

"As a researcher, I want to automate most steps in the workflow, to improve reproducibility and consistency in preprocessing and analyses."

"As a researcher, I want to inspect my (preprocessed) data as a quality measure."

"As a junior researcher, I want to execute a complex workflow with just one command."

"As a researcher, I want to generate plots of the EEG epochs and/or other features such as power spectral density and evoked responses."

"As a researcher, I want to plot variability of the signal for each frequency band in the EEG data to better understand neural processing."

"As a researcher, I want to plot signal differences in the Occipital lobe electrodes to investigate visual processing."

"As a researcher, I want to see how strong signal differences in three predefined brain regions are in order to understand localisation of processing in the brain.

"As a researcher, I want to generate statistical measures of the data and analyze them for effects."

"As a researcher, I want to generate spectograms to gain a better understanding of the time-domain of the data."

"As a senior researcher, I want to be able to customise each step of the workflow and be able to separately execute individual steps."


**Should have:**

"As a senior researcher, I want to automatically generate a PDF report, showing the results of the workflow."

"As a neurologist, I want to be able to selectively remove artifacts from the data, so as to not hinder further clinical analyses."

"As a researcher, I want to generate visualizations of the workflow to report them in the methods of a paper."

"As a researcher, I want to be able to run the workflow with a subset of data to test out the analyses."

**Could have:**

"As a researcher, I want to be able to apply transformations to the data to prepare it for further analyses."

"As an expert researcher, I want to transform the data into MNE forma because I'm familiar with it."

"As an expert researcher, I want to use the MNE format to integrate my own analyses/preprocessed data into the workflow."


**Won't have:**

"As a Data Scientist, I want to train ML models on the data."

"As a Data Scientist, I want to be able to specify parameters on what kind of model will be trained." 


### Summary

1. **Data Management**
   - The system must load, filter, and preprocess raw data to ensure it is clean and ready for analysis. This includes steps for noise reduction, artifact removal, and feature extraction.

2. **Analytical Processing**
   - The workflow must support various comparative analyses to identify significant differences and patterns within the data. These analyses should include comparisons based on predefined categories and criteria.

3. **Data Transformation**
   - The system should be capable of applying necessary transformations to the data, such as conversion into micro Volts or denoising, to prepare it for more detailed analysis.

4. **Result Generation**
   - The workflow must generate visualizations and reports to summarize and present the findings clearly and comprehensively. These outputs should be suitable for inclusion in scientific documentation and presentations.

5. **Automation and Efficiency**
   - The system should automate as many steps as possible to enhance efficiency and reduce the need for manual intervention, ensuring repeatability and consistency in the analysis.

### Non-Functional Requirements

1. **Performance**
   - The workflow should process data efficiently.
   - It must handle large datasets without performance degradation.

2. **Reliability**
   - Ensure accurate processing and analysis.
   - Handle errors gracefully and log issues.

3. **Usability**
   - Provide an intuitive interface for workflow configuration.
   - Include comprehensive documentation for each step.

4. **Maintainability**
   - Ensure steps are modular and maintainable.
   - Track changes with version control.

5. **Compatibility**
   - Ensure compatibility with various data formats and tools.
   - Ensure operability across different systems and environments.

### UML Activity Diagram

![Activity Diagram](activity_diagram.svg)
