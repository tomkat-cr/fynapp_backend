#!/bin/sh
# run_server_prod.sh
# 2022-03-10 | CR
# Parameters:
# $1 = $PORT (Heroku)
# $2 = Base dir [/app]
PORT=$1
BASE_DIR=$2
if [ "$BASE_DIR" = "" ]; then
    BASE_DIR="/app"
fi
mkdir -p ${BASE_DIR}/logs ;
touch ${BASE_DIR}/logs/fynapp_general.log
gunicorn -b 0.0.0.0:${PORT} --log-level debug -w 4 'fynapp_api.index:create_app()'
