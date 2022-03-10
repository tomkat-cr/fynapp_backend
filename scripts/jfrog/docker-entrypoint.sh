#!/bin/sh
# File: fynapp_backend/scripts/jfrog/docker-entrypoint.sh
# 2022-03-03 | CR
# Run:
# sh -x /var/scripts/docker-entrypoint.sh

# export GITLAB_ACCESS_TOKEN="<see docker-compose.yml file>" ;
# export GIT_REPO_PREFIX="<see docker-compose.yml file>"
# export GIT_REPO_NAME="<see docker-compose.yml file>"
# export GIT_REPO_BRANCH="<see docker-compose.yml file>"
export CI_PROJECT_DIR="/usr/src/app" ;

apt update
apt install -y git curl wget
apt install nano

# To fix "qemu: uncaught target signal 11 (Segmentation fault) - core dumped" running jfrog commands
# https://stackoverflow.com/questions/68862313/qemu-uncaught-target-signal-11-segmentation-fault-core-dumped-in-docker-con
# apt install -y qemu
# RESULT: this script cannot be run under a docker debian docker container using an M1 mac :(

# App directory
mkdir -p ${CI_PROJECT_DIR}

# Install jf CLI
# npm install -g jfrog-cli-v2-jf
# https://www.jfrog.com/confluence/display/CLI
# JFrog CLI v2 "jfrog" installers
wget -qO - https://releases.jfrog.io/artifactory/jfrog-gpg-public/jfrog_public_gpg.key | apt-key add -
echo "deb https://releases.jfrog.io/artifactory/jfrog-debs xenial contrib" | tee -a /etc/apt/sources.list;
apt update;
apt install -y jfrog-cli-v2;
jfrog -v

# upgrade npm to avoid ""summary": "Cannot destructure property 'dependencies' of 'node.package' as it is undefined."," error running the jfrog npm install command
# npm install -g npm@8.5.2

# Clone app
cd "${CI_PROJECT_DIR}"
git config --global credential.helper cache
# https://knasmueller.net/gitlab-authenticate-using-access-token
git clone "https://oauth2:${GITLAB_ACCESS_TOKEN}@${GIT_REPO_PREFIX}/${GIT_REPO_NAME}.git"
cd "${CI_PROJECT_DIR}/${GIT_REPO_NAME}"
git fetch
git checkout "${GIT_REPO_BRANCH}"

# leave it on bash (to keep the container running)
# bash

sh -x /var/scripts/jfrog_npm_build_publish.sh

