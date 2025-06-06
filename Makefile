# NOTE: make help uses a special comment format to group targets.
# If you'd like your target to show up use the following:
#
# my_target: ##@category_name sample description for my_target
default: help

.PHONY: install clean help

# If you have DOPPLER_TOKEN set in your environment, this codebase will attempt to use it.
# If you don't want to use it, make sure to unset it before running make commands.
# Variables
#$(shell _DT='${DOPPLER_TOKEN}'; echo "$${_DT}")
PYTHON := .python/bin/python
PACKAGE_NAME := $(shell ${PYTHON} scripts/get_project_directory.py)
PACKAGE_TYPE := $(shell ${PYTHON} scripts/get_app_type.py)
SERVICE_NAME := ${PACKAGE_NAME}
DOPPLER_PROJECT := ${DOPPLER_PROJECT}
DOPPLER_CONFIG := ${DOPPLER_CONFIG}
PORT := 8080
.EXPORT_ALL_VARIABLES:

############# Development Section #############
install: ##@meta Installs needed prerequisites and software to develop the project
	$(info ********** Installing Developer Tooling Prerequisites **********)
	@bash -l scripts/install.sh -a
	@bash -l scripts/install.sh -p
	@bash -l -c ".python/bin/python -m pip install --upgrade pip"
	@bash -l -c ".python/bin/python -m pip install -r requirements.txt"
	@asdf reshim
	@echo "[INFO] - You can now install the Cookie Cutter templates to your machine"
	@echo "[INFO] - Installation Complete!"

setup: ##@meta Sets up the application for development
	$(info ********** Setting up ${service_title} **********)
	@if [ ! -d .python ]; then echo "[ERROR] - Please install Python from the Makefile in root - run 'make install'"; exit 0; fi
	@bash -l scripts/setup-app.sh

run: ##@local Run the Service Locally
	$(info ********** Building Local ${SERVICE_TITLE} **********)
	@if [ ! -d .python ]; then echo "[ERROR] - Please install Python from the Makefile in root - run 'make install'"; exit 0; fi
	@bash scripts/entrypoint.sh -r

terminal: ##@local Run the Python REPL Locally
	@bash scripts/entrypoint.sh -t

build: ##@docker Build Docker Image (Local - Cloud Run Image)
	$(info ********** Building Local ${SERVICE_TITLE} Docker Image **********)
	@bash scripts/entrypoint.sh -b

start: ##@docker Run Docker Image (Local - Cloud Run Image)
	$(info ********** Running Local ${SERVICE_TITLE} Docker Image **********)
	@if [[ -z "$(docker image list | grep "${SERVICE_NAME}")" ]]; then echo "[ERROR] - Please run 'make build-docker' to build the Docker image." && exit 1; fi
	@bash scripts/entrypoint.sh -s

clean: ##@meta Cleans the project
	$(info ********** Cleaning ${service_title} **********)
	@rm -rf ./dev
	@rm -rf .pytest_cache
	@if [ -d ${HOME}/Library/Caches/pypoetry/virtualenvs ]; then rm -rf ${HOME}/Library/Caches/pypoetry/virtualenvs/${service}-*; fi

.PHONY: isort format
isort: ##@code Running isort on the project
	$(info ********** Decrypting Configuration File **********)
	@if [ ! -d ../.python ]; then echo "Please install Python from the Makefile in root - run 'make install'"; exit 0; fi
	@bash -l -c ".python/bin/python -m isort ."

format: ##@code Running black on the project
	$(info ********** Running Black on the project **********)
	@if [ ! -d ../.python ]; then echo "Please install Python from the Makefile in root - run 'make install'"; exit 0; fi
	@bash -l -c "./../.python/bin/python -m black ."

.PHONY: create-db
create-db: ##@code Running black on the project
	$(info ********** Creating ${service_title} Database/Tables **********)
	@bash scripts/build_sqlite_database.sh

help: ##@misc Show this help.
	@echo $(MAKEFILE_LIST)
	@perl -e '$(HELP_FUNC)' $(MAKEFILE_LIST)

# helper function for printing target annotations
# ripped from https://gist.github.com/prwhite/8168133
HELP_FUNC = \
	%help; \
	while(<>) { \
		if(/^([a-z0-9_-]+):.*\#\#(?:@(\w+))?\s(.*)$$/) { \
			push(@{$$help{$$2}}, [$$1, $$3]); \
		} \
	}; \
	print "usage: make [target]\n\n"; \
	for ( sort keys %help ) { \
		print "$$_:\n"; \
		printf("  %-20s %s\n", $$_->[0], $$_->[1]) for @{$$help{$$_}}; \
		print "\n"; \
	}
