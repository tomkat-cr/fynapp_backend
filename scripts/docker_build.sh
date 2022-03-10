#!/bin/bash
# File: fynapp_backend/scripts/docker_build.sh
# 2022-02-25 | CR
# Run: source docker_build.sh
# Then: source docker_push.sh
#
# Parameters
. "`dirname "$0"`/docker_build_vars.sh" $1
# Build it
echo "[BE] Docker build this: ${DOCKER_ACCOUNT}/${DOCKER_APP_NAME}:${DOCKER_APP_VERSION}"
docker build --platform=linux/amd64 -t ${DOCKER_ACCOUNT}/${DOCKER_APP_NAME}:${DOCKER_APP_VERSION} "`dirname "$0"`/.."
# Test it
echo "[BE] To test the build: ${DOCKER_ACCOUNT}/${DOCKER_APP_NAME}:${DOCKER_APP_VERSION}"
echo "docker run -p ${DOCKER_APP_PORTS} ${DOCKER_ACCOUNT}/${DOCKER_APP_NAME}:${DOCKER_APP_VERSION}"
