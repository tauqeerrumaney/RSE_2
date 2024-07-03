#!/usr/bin/make -f

# Variables
CONFIG_DIR=config
CONFIG_FILE=$(CONFIG_DIR)/config.yaml
CONFIG_EXAMPLE=$(CONFIG_FILE).example
WORKFLOW_DIR=workflow
SCRIPTS_DIR=$(WORKFLOW_DIR)/scripts

# Default target
.PHONY: all
all: copy_config run_snakemake

# Copy config file
.PHONY: copy_config
copy_config:
	@if [ ! -f $(CONFIG_FILE) ]; then \
		cp $(CONFIG_EXAMPLE) $(CONFIG_FILE); \
	fi

# Run Snakemake
.PHONY: run_snakemake
run_snakemake:
	snakemake --use-conda --cores all

# Lint step
.PHONY: lint
lint:
	snakefmt $(WORKFLOW_DIR)/
	snakemake --lint
	autopep8 --in-place -a -a -r $(SCRIPTS_DIR)/
	flake8 $(SCRIPTS_DIR)/

# Clean step
.PHONY: clean
clean:
	snakemake --use-conda --cores 1 clean

# Plot workflow
.PHONY: plot
plot:
	snakemake --use-conda --cores 1 plot_dag
