#!/bin/sh
# run_server.sh
# 2022-02-18 | CR
if [ -f ".env" ] ; then
    set -o allexport; . .env ; set +o allexport ;
fi

python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt

gunicorn -b 0.0.0.0:5001 --log-level debug -w 4 'fynapp_api.__init__:create_app()'

# Ports in use
# sudo lsof -PiTCP -sTCP:LISTEN