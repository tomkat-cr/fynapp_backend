#!/bin/sh
# File: fynapp_backend/scripts/mongo/db_mongo_backup.sh
# 2022-03-12 | CR
# Prerequisite: yum/apt/brew install mongodb-database-tools
#
cd "`dirname "$0"`" ;
SCRIPTS_DIR="`pwd`" ;
cd ../.. # set repo root as current dir
if [ -f ".env" ]; then
    set -o allexport; . ".env"; set +o allexport ;
fi
DO_RESTORE=1
if [ "$1" = "" ]; then
    echo "";
    echo "ERROR: Database name must be supplied";
    echo "";
    DO_RESTORE=0
fi
if [ "${FYNAPP_DB_URI}" = "" ]; then
    echo "";
    echo "ERROR: FYNAPP_DB_URI must be set";
    echo "";
    DO_RESTORE=0
fi
if [ ${DO_RESTORE} -eq 1 ]; then
    echo "";
    echo "Backup database: $1";
    echo "";
    mongodump --uri ${FYNAPP_DB_URI}/$1 ;
    echo "";
    echo "Dump/$1 directory content:";
    echo "";
    ls -lah ./dump/$1
    echo "";
fi
