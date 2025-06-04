# NOTE: make help uses a special comment format to group targets.
# If you'd like your target to show up use the following:
#
# my_target: ##@category_name sample description for my_target
default: help

.PHONY: install clean help

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
	@bash -l scripts/setup-app.sh

run: ##@run Run the Service Locally
	$(info ********** Building Local ${SERVICE_TITLE} **********)
	@doppler run --project ${DOPPLER_PROJECT} --config ${DOPPLER_CONFIG} --token ${_DOPPLER_TOKEN} --command "./.python/bin/python -m poetry run uvicorn ${PACKAGE_NAME}:app --host 0.0.0.0 --port ${PORT} --reload"

terminal: ##@run Run the Python REPL Locally
	@doppler run --project ${DOPPLER_PROJECT} --config ${DOPPLER_CONFIG} --token ${_DOPPLER_TOKEN} --command "./.python/bin/python -m poetry run python"

build-docker: ##@build Build Docker Image (Local - Cloud Run Image)
	$(info ********** Building Local ${SERVICE_TITLE} Docker Image **********)
	@make build
	@if [[ -z "${_DOPPLER_TOKEN}" ]]; then echo "[ERROR] - DOPPLER_TOKEN is not set. Please set the DOPPLER_TOKEN environment variable." && exit 1; fi
	@docker build --build-arg="SERVICE_NAME=${SERVICE_NAME}" --build-arg="DOPPLER_PROJECT=${DOPPLER_PROJECT}" --build-arg="DOPPLER_CONFIG=${DOPPLER_CONFIG}" --build-arg="DOPPLER_TOKEN=${DOPPLER_TOKEN}" -t ${SERVICE_NAME}:local --file Dockerfile .

run-docker: ##@run Run Docker Image (Local - Cloud Run Image)
	$(info ********** Running Local ${SERVICE_TITLE} Docker Image **********)
	@if [[ -z "$(docker image list | grep "${SERVICE_NAME}")" ]]; then echo "[ERROR] - Please run 'make build-docker' to build the Docker image." && exit 1; fi
	@docker run -p 8080:8080/tcp -it --rm --name ${SERVICE_NAME} ${SERVICE_NAME}:local

clean: ##@meta Cleans the project
	$(info ********** Cleaning ${service_title} **********)
	@rm -rf ./dev
	@rm -rf .pytest_cache
	@if [ -d ${HOME}/Library/Caches/pypoetry/virtualenvs ]; then rm -rf ${HOME}/Library/Caches/pypoetry/virtualenvs/${service}-*; fi

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
