#!/usr/bin/env bash
# Copyright (c) 2025, PyFlowOps

# This script is basically the entrypoint for the Makefile
# It is used to keep the Makefile clean and simple

set -eou pipefail
shopt -s expand_aliases

BASE="$(dirname ${BASH_SOURCE[0]})"
BASEDIR="$(realpath ${BASE}/..)"
_GROUP=$(groups | awk -F' ' '{print $1}')
DOPPLER_TOKEN=${DOPPLER_TOKEN:-}
PACKAGE_NAME=${PACKAGE_NAME:-} # This is set in the Makefile - get_project_directory.py
SERVICE_NAME=${SERVICE_NAME:-} # This is set in the Makefile
PORT=${PORT:-8000} # Default port for the application, this is set in the Makefile

# Check if Doppler Token is set, run the commands wrapped if so
[[ -z ${DOPPLER_TOKEN} ]] && {
    echo "[INFO] - Doppler Token is NOT set, running commands without Doppler"
   _DT=false
} || {
    echo "[INFO] - Doppler Token is set, running commands with Doppler"
    _DT=true
}

# We need to make sure that the PACKAGE_NAME is set correctly, this is the name of the package we are running
[[ -z ${PACKAGE_NAME} ]] || [[ ${PACKAGE_NAME} == *"[WARN]"* ]] && {
    echo "[ERROR] - PACKAGE_NAME == '${PACKAGE_NAME}'; please install a package to the repo."
    exit 0
}

# If the Doppler Token is set, we also need to have the DOPPLER_PROJECT, and DOPPLER_CONFIG
[[ "${_DT}" == "true" ]] && {
    # If the service token type is service_token, then we only need the token
    # If it is a service account, or a personal token then we need the project and config
    _script_type=$(${BASEDIR}/.python/bin/python ${BASE}/service_token_type.py)

    if [[ "${_script_type}" != "service_token" ]]; then
        [[ -z "${DOPPLER_PROJECT:-}" ]] && {
            echo "[ERROR] - DOPPLER_PROJECT is not set, please set it to the project you want to use"
            exit 0
        }
        [[ -z "${DOPPLER_CONFIG:-}" ]] && {
            echo "[ERROR] - DOPPLER_CONFIG is not set, please set it to the config you want to use"
            exit 0
        }
    fi
}

run()
{
    # Add the plugin in asdf
    [[ "${_DT}" == true ]] && {
        echo "[INFO] - Running commands with Doppler"
        # With a service token, the token is scoped to the project AND config - so there is no need to have them set in the environment
        if [[ "${_script_type}" == "service_token" ]]; then
            doppler run --token ${DOPPLER_TOKEN} --command "./.python/bin/poetry run uvicorn ${PACKAGE_NAME}:app --host 0.0.0.0 --port ${PORT} --reload"
        else
            doppler run --project ${DOPPLER_PROJECT} --config ${DOPPLER_CONFIG} --token ${DOPPLER_TOKEN} --command "./.python/bin/python -m poetry run uvicorn ${PACKAGE_NAME}:app --host 0.0.0.0 --port ${PORT} --reload"
        fi
    } || {
        echo "[INFO] - Running commands without Doppler"
        cd "${BASEDIR}" || exit 1 && ./.python/bin/poetry run uvicorn ${PACKAGE_NAME}:app --host 0.0.0.0 --port ${PORT} --reload
    }
}

terminal()
{
    # Add the plugin in asdf
    [[ "${_DT}" == true ]] && {
        echo "[INFO] - Running commands with Doppler"
        # With a service token, the token is scoped to the project AND config - so there is no need to have them set in the environment
        if [[ "${_script_type}" == "service_token" ]]; then
            doppler run --token ${DOPPLER_TOKEN} --command "./.python/bin/python -m poetry run python"
        else
            doppler run --project ${DOPPLER_PROJECT} --config ${DOPPLER_CONFIG} --token ${DOPPLER_TOKEN} --command  "./.python/bin/python -m poetry run python"
        fi
    } || {
        echo "[INFO] - Running commands without Doppler"
        cd "${BASEDIR}" || exit 1 && ./.python/bin/poetry run uvicorn ${PACKAGE_NAME}:app --host 0.0.0.0 --port ${PORT} --reload
    }
}

docker_build()
{
    [[ -f "${BASEDIR}/${PACKAGE_NAME}/Dockerfile" ]] || {
        echo "[ERROR] - Dockerfile not found in ${BASEDIR}, please make sure it exists"
        exit 0
    }
    # Add the plugin in asdf
    [[ "${_DT}" == true ]] && {
        echo "[INFO] - Running Docker commands with Doppler"
        # With a service token, the token is scoped to the project AND config - so there is no need to have them set in the environment
        if [[ "${_script_type}" == "service_token" ]]; then
	        docker build --build-arg="SERVICE_NAME=${SERVICE_NAME}" \
                --build-arg="DOPPLER_TOKEN=${DOPPLER_TOKEN}" \
                -t ${SERVICE_NAME}:local \
                --file Dockerfile .
        else
	        docker build --build-arg="SERVICE_NAME=${SERVICE_NAME}" \
                --build-arg="DOPPLER_PROJECT=${DOPPLER_PROJECT}" \
                --build-arg="DOPPLER_CONFIG=${DOPPLER_CONFIG}" \
                --build-arg="DOPPLER_TOKEN=${DOPPLER_TOKEN}" \
                -t ${SERVICE_NAME}:local \
                --file Dockerfile .
        fi
    } || {
        echo "[INFO] - Running Docker command without Doppler"
        docker build --build-arg="SERVICE_NAME=${SERVICE_NAME}" -t ${SERVICE_NAME}:local --file Dockerfile .
    }
}

docker_start()
{
    [[ -f "${BASEDIR}/${PACKAGE_NAME}/Dockerfile" ]] || {
        echo "[ERROR] - Dockerfile not found in ${BASEDIR}, please make sure it exists"
        exit 0
    }
    docker run -p ${PORT}:${PORT}/tcp -it --rm --name ${SERVICE_NAME} ${SERVICE_NAME}:local
}

completed()
{
    echo "[INFO] - Script complete!"
}

usage() { echo "Usage: $0 [-a asdf] [-p [Python Install Flag]]" 1>&2; exit 1; }

while getopts ":rpbs" arg; do
    case "${arg}" in
        r)
            run
            completed
            ;;
        t)
            terminal
            completed
            ;;
        b)
            docker_build
            completed
            ;;
        s)
            docker_start
            completed
            ;;
        \?)
            echo "[ERROR] - Unknown flag passed"
            usage
            ;;
        :)
            echo "[ERROR] - Option -${arg} requires an argument." >&2
            exit 1
            ;;
        *)
            usage
            ;;
    esac
done

unset_data()
{
    unset _GROUP
    unset DOPPLER_TOKEN
    unset PACKAGE_NAME
    unset SERVICE_NAME
    unset PORT
    unset _script_type
    unset BASE
    unset _DT
    unset LOCATION
    unset _PUBLICFILENAME
}

# Let's clean up the data.
unset_data

shift $((OPTIND-1))
