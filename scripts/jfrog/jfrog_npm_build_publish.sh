#!/bin/bash
# File: fynapp_backend/scripts/jfrog/jfrog_npm_build_publish.sh
# 2022-03-02 | CR
# Run: sh -x /var/scripts/jfrog/jfrog_npm_build_publish.sh

SCRIPTS_DIR="`dirname "$0"`"

# Variables
if [ -f "${SCRIPTS_DIR}/.env" ]; then
    set -o allexport; . "${SCRIPTS_DIR}/.env"; set +o allexport ;
fi

# export PYPI_USERNAME="ver docker-compose.yml"
# export PYPI_PASSWORD="ver docker-compose.yml"
# export GIT_REPO_NAME="ver docker-compose.yml"
# export JFROG_URL="ver docker-compose.yml"
# export ARTIFACTORY_REPO="ver docker-compose.yml"
# export ARTIFACTORY_REPO_AUTH="ver docker-compose.yml"
# export ARTIFACTORY_EMAIL="ver docker-compose.yml"

if [ "${CI_PROJECT_DIR}" = "" ]; then
    export CI_PROJECT_DIR="/usr/src/app" ;
fi
cd "${CI_PROJECT_DIR}/${GIT_REPO_NAME}"

# App version
export APP_VERSION="`cat "../../version.txt"`"
if [ "${APP_VERSION}" != "" ]; then
    export ARTIFACTORY_BUILD_NUMBER="${APP_VERSION}" ;
fi

# PRE-REQUISITES
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt

# To deploy packages using setuptools you need to add an Artifactory repository to the .pypirc file (usually located in your home directory):

echo "" > ~/.pypirc
echo "[distutils]" >> ~/.pypirc
echo "index-servers =" >> ~/.pypirc
echo "    local" >> ~/.pypirc
echo "    pypi" >> ~/.pypirc

echo "[pypi]" >> ~/.pypirc
echo "repository: https://pypi.org/pypi" >> ~/.pypirc
echo "username: ${PYPI_USERNAME}" >> ~/.pypirc
echo "password: ${PYPI_PASSWORD}" >> ~/.pypirc

echo "[local]" >> ~/.pypirc
echo "repository: ${JFROG_URL}/artifactory/api/pypi/${ARTIFACTORY_REPO}" >> ~/.pypirc
echo "username: ${ARTIFACTORY_EMAIL}" >> ~/.pypirc
echo "password: ${ARTIFACTORY_REPO_AUTH}" >> ~/.pypirc

# Uploading
# To deploy a python egg to Artifactory, after changing the .pypirc file, run the following command:

python setup.py sdist upload -r local

# To deploy a python wheel to Artifactory, after changing the .pypirc file, run the following command:

python setup.py bdist_wheel upload -r local

# where `local` is the index server you defined in .pypirc.

rm ~/.pypirc