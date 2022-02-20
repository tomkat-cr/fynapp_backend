#!/bin/sh
#
# sh $HOME/desarrollo/mediabros_repos/fynapp_backend/run_fynapp_backend_tests.sh
# 2022-02-17 | CR
#
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
pip install pytest coverage
python -m pytest
deactivate

