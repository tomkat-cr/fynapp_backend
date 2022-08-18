#!/bin/bash
# File: fynapp_backend/scripts/jfrog/jfrog_npm_build_publish.sh
# 2022-03-02 | CR
# Run: sh -x /var/scripts/jfrog/jfrog_npm_build_publish.sh

# SCRIPTS_DIR="`dirname "$0"`"
cd "`dirname "$0"`" ;
SCRIPTS_DIR="`pwd`" ;
echo "SCRIPTS_DIR = ${SCRIPTS_DIR}";

echo "";
echo "*| Reading parameters from .env |*";
echo "";

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

echo "";
echo "*| Moving to project root directory |*";
echo "";

if [ "${CI_PROJECT_DIR}" = "" ]; then
    # export CI_PROJECT_DIR="/usr/src/app" ;
    export CI_PROJECT_DIR="${SCRIPTS_DIR}/../.." ;
fi
echo "CI_PROJECT_DIR/GIT_REPO_NAME = ${CI_PROJECT_DIR}/${GIT_REPO_NAME}";
cd "${CI_PROJECT_DIR}/${GIT_REPO_NAME}"
echo "Current Dir: `pwd`";

# App version

echo "";
echo "*| Getting App version |*";
echo "";

export APP_VERSION="`cat "version.txt"`"
if [ "${APP_VERSION}" != "" ]; then
    export ARTIFACTORY_BUILD_NUMBER="${APP_VERSION}" ;
fi
echo "ARTIFACTORY_BUILD_NUMBER = ${ARTIFACTORY_BUILD_NUMBER}";

# PRE-REQUISITES

echo "";
echo "*| Activating Venv and performing pip install |*";
echo "";

python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt

# To deploy packages using setuptools you need to add an Artifactory repository to the .pypirc file (usually located in your home directory):

echo "";
echo "*| Creating ~/.pypirc |*";
echo "";

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

ls -lah ~/.pypirc ;

# Uploading
# To deploy a python egg to Artifactory, after changing the .pypirc file, run the following command:

echo "";
echo "*| Deploy Python Egg to Artifactory |*";
echo "";

python setup.py sdist upload -r local

# To deploy a python wheel to Artifactory, after changing the .pypirc file, run the following command:

echo "";
echo "*| Deploy Python Wheel to Artifactory |*";
echo "";

python setup.py bdist_wheel upload -r local

# where `local` is the index server you defined in .pypirc.

echo "";
echo "*| Spring cleaning: remove ~/.pypirc |*";
echo "";

rm ~/.pypirc
