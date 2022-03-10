#!/bin/bash
# "fynapp_backend/scripts/vps/deploy_to_vps.sh"
#
CURRENT_DIR="`dirname "$0"`"
cd "${CURRENT_DIR}" ;

# Set app version if 1st parameter is passed to this script
if [ "$1" != "" ]; then
    echo $1 > version.txt
fi

VPS_USER="ocrusr"
if [ "$2" != "" ]; then
    VPS_USER=$2
fi

VPS_NAME="vps.fynapp.com"
if [ "$3" != "" ]; then
    VPS_NAME=$3
fi

VPS_PORT="33007"
if [ "$4" != "" ]; then
    VPS_PORT=$4
fi

LOCAL_PRIVATE_KEY_PATH="~/.ssh/id_rsa_${VPS_USER}_${VPS_NAME}"
if [ "$5" != "" ]; then
    LOCAL_PRIVATE_KEY_PATH=$5
fi

VPS_DIRECTORY="~/fynapp_start_be"
if [ "$6" != "" ]; then
    VPS_DIRECTORY=$6
fi

# Variables
SSH_CMD="ssh -p ${VPS_PORT} -i ${LOCAL_PRIVATE_KEY_PATH} -oStrictHostKeyChecking=no"

echo "" > .env
echo "FLASK_APP=$FLASK_APP" >> .env;
echo "FLASK_ENV=$FLASK_ENV" >> .env;
echo "FLASK_DEBUG=$FLASK_DEBUG" >> .env;
echo "FYNAPP_DB_NAME=$FYNAPP_DB_NAME" >> .env;
echo "FYNAPP_DB_URI=$FYNAPP_DB_URI" >> .env;
echo "FYNAPP_SECRET_KEY=$FYNAPP_SECRET_KEY" >> .env;

# Copy minimum files to bring up the containers
rsync -arv -e "${SSH_CMD}" ./.env ${VPS_USER}@${VPS_NAME}:${VPS_DIRECTORY}/
rsync -arv -e "${SSH_CMD}" ./* ${VPS_USER}@${VPS_NAME}:${VPS_DIRECTORY}/

# Restart the containers on thee VPS
${SSH_CMD} ${VPS_USER}@${VPS_NAME} "sh -x ${VPS_DIRECTORY}/run-server-containers.sh down"
${SSH_CMD} ${VPS_USER}@${VPS_NAME} "sh -x ${VPS_DIRECTORY}/run-server-containers.sh '' rmi"

# Clean up
if [ -f version.txt ]; then
    rm version.txt
fi
rm .env
