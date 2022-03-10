#!/bin/bash
# File: fynapp_backend/scripts/docker_install_deps.sh
# 2022-02-25 | CR
# Run: source docker_install_deps.sh
apt update -qy
apt install -y pipenv
