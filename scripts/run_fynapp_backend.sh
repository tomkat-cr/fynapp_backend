#!/bin/sh
#
# source $HOME/desarrollo/mediabros_repos/fynapp_backend/run_fynapp_backend.sh
# 2021-08-07 | CR
#
# Especifica donde esta este script, que debe ser el directorio del repositorio...
cd "`dirname "$0"`" ;
SCRIPTS_DIR="`pwd`" ;
REPO_BASEDIR="${SCRIPTS_DIR}/.."
#
# Credenciales desde un .env (deberian ir mas bien en un "Vault")
if [ -f "${REPO_BASEDIR}/.env" ]; then
    set -o allexport; . "${REPO_BASEDIR}/.env"; set +o allexport ;
fi
if [[ "${FYNAPP_DB_USR_PSW}" == "" ]]; then 
    # Si no encontro las credenciales en el .env, intenta sacarlas de 1Password
    OP_ENTRY_NAME_MONGO_CREDS="MongoDB Atlas MBI Fynapp-Dev Admin"
    OP_ENTRY_NAME_FYNAPP_SECRET_KEY="Fynapp Secret Key JWT"
    # Verifica si hay una sesion abierta de 1Password, si no, login.
    while [[ "${OP_SESSION_my}" == "" ]]; do
        export OP_SESSION_my=$(op signin my -r)
    done
    OP_TEST=$(op get item --fields password "${OP_ENTRY_NAME_MONGO_CREDS}")
    if [[ "$?" != 0 ]]; then
        export OP_SESSION_my=$(op signin my.1password.com -r)
    fi
    OP_TEST=$(op get item --fields password "${OP_ENTRY_NAME_MONGO_CREDS}")
    if [[ "$?" != 0 ]]; then
        unset OP_SESSION_my
        echo -e " \e[91m>> La sesión de 1Password expiró. Ejecute de nuevo 'op signin my.1password.com yourname@yourmailserver.com <secret_key_from_pdf>'"
        return 1
    fi
    FYNAPP_DB_USR_NAME=$(op get item --fields username "${OP_ENTRY_NAME_MONGO_CREDS}")
    FYNAPP_DB_USR_PSW=$(op get item --fields password "${OP_ENTRY_NAME_MONGO_CREDS}")
    export FYNAPP_SECRET_KEY=$(op get item --fields credential "${OP_ENTRY_NAME_FYNAPP_SECRET_KEY}")
fi
if [[ "${FYNAPP_DB_USR_PSW}" == "" ]]; then 
    echo "No fue posible obtener el nombre de usuario para MongoDb"
    # exit 1
else
    if [[ "${FYNAPP_SECRET_KEY}" == "" ]]; then 
        echo "No fue posible obtener el el app secret key"
        # exit 1
    else
        #
        export FLASK_APP="fynapp_api"
        export FLASK_ENV="development"
        export FYNAPP_DB_ENV="dev"
        export FYNAPP_DB_SERVER="fynapp-cl.q1czd.mongodb.net"
        export FYNAPP_DB_NAME="fynapp_${FYNAPP_DB_ENV}"
        export FYNAPP_DB_URI="mongodb+srv://${FYNAPP_DB_USR_NAME}:${FYNAPP_DB_USR_PSW}@${FYNAPP_DB_SERVER}"
        #
        cd ${REPO_BASEDIR}
        python3 -m venv venv
        source venv/bin/activate
        pip3 install -r requirements.txt
        if [[ "$1" == "test" ]]; then 
            pip install pytest coverage
            python -m pytest
        else
            flask run
            deactivate
        fi
    fi
fi
