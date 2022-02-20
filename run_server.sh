#!/bin/sh
# run_server.sh
# 2022-02-18 | CR
set -o allexport; source .env ; set +o allexport ;

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# gunicorn -b 127.0.0.1:5000 --log-level debug -w 4 fynapp_api:__init__
# gunicorn -b 127.0.0.1:5000 --log-level debug -w 4 fynapp_api.app:app
gunicorn -b 127.0.0.1:5000 --log-level debug -w 4 'fynapp_api.__init__:create_app()'

# gunicorn -b localhost:5000 -b 0.0.0.0:5000 --log-level debug -w 4 --proxy-protocol --proxy-allow-from 127.0.0.1,localhost fynapp_api:__init__
# gunicorn --config fynapp_api/gunicorn_config.py fynapp_api:__init__ 

# Ports in use
# sudo lsof -PiTCP -sTCP:LISTEN