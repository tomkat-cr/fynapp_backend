#!/bin/bash
# File: "fynapp_frontend/scripts/vps/local_test.sh"
# Nota: ejecutar este script desde la raiz del repositorio...

export APP_VERSION="`cat "version.txt"`"

# export LOCAL_PRIVATE_KEY_PATH="./id_rsa_${VPS_USER}_${VPS_NAME}"
# echo $VPS_PRIVATE_KEY_FILE > $LOCAL_PRIVATE_KEY_PATH
# chmod 600 $LOCAL_PRIVATE_KEY_PATH
if [ -f "scripts/vps/.env.local" ]; then
    set -o allexport; . "scripts/vps/.env.local" ; set +o allexport ;
fi

apt install -y pipenv
pipenv install
sh scripts/docker_build.sh $APP_VERSION
sh scripts/docker_push.sh $DOCKER_ACCOUNT $DOCKER_PASSWORD $APP_VERSION
sh scripts/vps/deploy_to_vps.sh $APP_VERSION $VPS_USER $VPS_NAME $VPS_PORT $LOCAL_PRIVATE_KEY_PATH
