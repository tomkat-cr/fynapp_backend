#!/bin/bash
# File: fynapp_backend/scripts/docker_push.sh
# 2022-02-25 | CR
# Previous run: source docker_build.sh
# Then run: source docker_push.sh
. "`dirname "$0"`/docker_build_vars.sh" $3
if [ "$1" != "" ]; then
    export DOCKER_ACCOUNT="$1";
fi
if [ "$2" != "" ]; then
    export DOCKER_PASSWORD="$2";
fi
echo "[BE] Docker pushing this: ${DOCKER_ACCOUNT}/${DOCKER_APP_NAME}:${DOCKER_APP_VERSION}"
echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_ACCOUNT}" --password-stdin
# docker login -u ${DOCKER_ACCOUNT} -p ${DOCKER_PASSWORD}
docker push ${DOCKER_ACCOUNT}/${DOCKER_APP_NAME}:${DOCKER_APP_VERSION}
