#!/bin/sh
#
# sh $HOME/desarrollo/mediabros_repos/fynapp_backend/run_fynapp_backend_tests.sh
# 2022-02-17 | CR
#
cd "`dirname "$0"`" ;
SCRIPTS_DIR="`pwd`" ;
REPO_BASEDIR="${SCRIPTS_DIR}/.."
cd "${REPO_BASEDIR}"
if [ -f "${REPO_BASEDIR}/.env" ]; then
    set -o allexport; . "${REPO_BASEDIR}/.env"; set +o allexport ;
fi
#
PERFORM_TEST=1
if docker-compose -f test/mongodb_stack_for_test.yml up -d
then
    export FYNAPP_DB_URI=mongodb://root:example@127.0.0.1 ;
    docker ps ;
else
    PERFORM_TEST=0 ;
    echo "PERFORM_TEST=${PERFORM_TEST}"
fi
#
if [ ${PERFORM_TEST} -eq 1 ]; then
    python3 -m venv venv ;
    source venv/bin/activate ;
    pip3 install -r requirements.txt ;
    pip install pytest coverage ;
    python -m pytest ;
    deactivate ;
fi
docker-compose -f test/mongodb_stack_for_test.yml down ;
