# RSE Project 2

This is the second project in the 2024 course "Research Software Engineering" at the University of Potsdam. For more information, see the [requirements document](docs/requirements.md).

## Table of Contents
1. [Usage](#usage)
1. [Data Source and License](#data-source-and-license)
1. [Contributing Guidelines](#contributing-guidelines)
1. [Contact Information](#contact-information)
1. [Citation](#citation)
1. [License](#license)

## Usage

Ensure you have the following prerequisites installed on your system:

- **[Conda](https://docs.anaconda.com/miniconda/)**: For environment management.
- **[Snakemake](https://snakemake.readthedocs.io/en/stable/)**: For workflow management.

### Running the Workflow

To run the entire workflow, execute the following command from the root directory of the repository:

```sh
make
```

This command will initiate the workflow and handle all necessary steps automatically. Upon the first run, a configuration file (`config/config.yaml`) will be created if it does not already exist.

### Configuration

The configuration file (`config/config.yaml`) contains settings that can be customized to suit your needs:

- **Use a Reduced Dataset for Testing**:
  ```yaml
  mock: false
  ```
  Set `mock` to `true` to use a smaller dataset for testing purposes.

- **Exclude Specific Artifacts**:
  ```yaml
  artifacts: "1,3,5"
  ```
  Provide a comma-separated list of artifact IDs to exclude from the workflow.

### Cleaning Up

To remove all generated output and clean the output directories, use the following command:

```sh
make clean
```

### Running Specific Steps

To run specific steps of the workflow, use Snakemake's targeted execution:
```sh
snakemake <target_rule>
```

If you wish to run a script or command outside of the workflow, you can activate the specific Conda environment manually:
```sh
conda env create --name <environment_name> -f workflow/envs/<environment_file>.yaml
conda activate <environment_name>
# Run your script or command here
```

For example, to run the Independent Component Analysis (ICA) script:
```sh
conda env create -f workflow/envs/ica.yaml
conda activate rse24_project-two_ica
python workflow/scripts/ica.py temp/truncated_data.feather ica_epo.fif plot.png
```

### Developer Guide

For developers looking to contribute or maintain the project, the following commands are available:

**Lint the Workflow**:
Ensure you have `snakefmt`, `autopep8`, and `flake8` installed. Run the following command to format and check the code:

```sh
make lint
```

**Generate Workflow Diagram**:
Create a visual representation of the workflow with:

```sh
make plot
```

## Data Source and License
- Data sources: Detailed information on where the data is sourced from.
- Data license: Information on how the data is licensed.

## Contributing Guidelines
If you wish to contribute to the project, please review the [contribution guidelines](CONTRIBUTING.md) and the [code of conduct](CONDUCT.md). By participating, you are expected to adhere to these guidelines.

We use the [issues tab](https://gitup.uni-potsdam.de/werner10/rse24_project-two/-/issues) for tracking features and bugs.

## Contact Information
For any inquiries, please contact us at:
- [Harshini Eggoni](mailto:eggoni@uni-potsdam.de)
- [Philipp Freiherr von Entreß-Fürsteneck](mailto:entressfue@uni-potsdam.de)
- [Max Nowaczyk](mailto:nowaczyk@uni-potsdam.de)
- [Tauqeer Kasam Rumaney](mailto:rumaney@uni-potsdam.de)
- [Tim Werner](mailto:tim.werner@uni-potsdam.de)

## Citation
For information on how to cite this project, please refer to the [citation file](CITATION.cff).

## License
This project is licensed under the [MIT License](LICENSE).
