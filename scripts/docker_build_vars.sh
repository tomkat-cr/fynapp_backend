#!/bin/bash
# File: fynapp_backend/scripts/docker_build_vars.sh
# 2022-02-25 | CR
#
# Parameters
if [ "$1" != "" ]; then
    export APP_VERSION="$1";
else
    CURRENT_DIR="`dirname "$0"`";
    export APP_VERSION="${CURRENT_DIR}/../../version.txt"
fi
export DOCKER_ACCOUNT="mediabros"
# export DOCKER_PASSWORD="xxx" # Defined on the CI/CD Secure Variables
export DOCKER_APP_NAME="fynapp_backend"
export DOCKER_APP_VERSION="v${APP_VERSION}-amd64"
export DOCKER_APP_PORTS="5000:5000"
