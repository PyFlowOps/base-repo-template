#!/usr/bin/env bash
# Copyright (c) 2025, PyFlowOps
set -eou pipefail

# Real path of the script/..
BASE="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"
REPO="$(realpath ${BASE}/..)"

shopt -s expand_aliases

DIR="$(${REPO}/.python/bin/python ${BASE}/get_project_directory.py)"

function help() {
    echo "[ERROR] - The pyproject.toml file not found in the repository: There is no app created, please create your application first."
    echo "[CRITICAL] - This repo needs a project, or to be managed with the pfo CLI."
    echo "[CRITICAL] - Please create a project using the pfo CLI, or manage this repo with the pfo CLI."
}

# If the [WARN] message is shown, it means there is no current project in the repo.
[[ ${DIR} == *"[WARN]"* ]] && echo "${DIR}" && help && exit 0

# Let's make sure that the directory found is actually a valid directory
[[ ! -d "${REPO}/${DIR}" ]] && echo "[ERROR] - The directory found is not a valid directory: ${REPO}/${DIR}" && help && exit 1

# Project was found, continue logic here
echo "[INFO] - Installing Poetry dependencies for the project: ${DIR}"
cd ${REPO}/${DIR} || exit 1 && .python/bin/poetry install
echo "[INFO] - Application Setup Complete!"
