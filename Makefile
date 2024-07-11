#!/usr/bin/make -f

# Variables
CONFIG_DIR=config
CONFIG_FILE=$(CONFIG_DIR)/config.yaml
CONFIG_EXAMPLE=$(CONFIG_FILE).example
WORKFLOW_DIR=workflow
SCRIPTS_DIR=$(WORKFLOW_DIR)/scripts
TESTS_DIR=tests

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
	autopep8 --in-place -a -a -r $(SCRIPTS_DIR)/ $(TESTS_DIR)/
	flake8 $(SCRIPTS_DIR)/ $(TESTS_DIR)/

# Clean step
.PHONY: clean
clean:
	rm -rf temp/ results/ logs/

# Plot workflow
.PHONY: plot
plot:
	snakemake -c 1 --dag | dot -Tpng -o docs/dag.png

# Test step
.PHONY: test
test:
	@if conda env list | grep -q rse24_project-two_test; then \
		conda env update -f tests/test_env.yaml --prune; \
	else \
		conda env create -f tests/test_env.yaml; \
	fi
	conda run -n rse24_project-two_test \
		pytest ${TESTS_DIR}
	conda env remove -n rse24_project-two_test -y
