#!/bin/sh
# run_vercel.sh
APP_DIR='chalicelib'
PYTHON3_EXEC='/usr/local/bin/python3.9'
RUN_AS_MODULE=1
ENV_FILESPEC=""
if [ -f "./.env" ]; then
    ENV_FILESPEC="./.env"
fi
if [ -f "../.env" ]; then
    ENV_FILESPEC="../.env"
fi
if [ "$ENV_FILESPEC" != "" ]; then
    set -o allexport; source ${ENV_FILESPEC}; set +o allexport ;
fi
if [ "$PORT" = "" ]; then
    PORT="5001"
fi
if [ "$1" = "deactivate" ]; then
    cd ${APP_DIR} ;
    deactivate ;
fi
if [[ "$1" != "deactivate" && "$1" != "pipfile" && "$1" != "clean" ]]; then
    ${PYTHON3_EXEC} -m venv ${APP_DIR} ;
    . ${APP_DIR}/bin/activate ;
    cd ${APP_DIR} ;
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip install "attrs==21.2.0"
        pip install "boto3==1.24.55"
        pip install "botocore==1.27.55"
        pip install "certifi==2018.11.29"
        pip install "cffi==1.15.0"
        pip install "click==8.0.3"
        pip install "cryptography==35.0.0"
        pip install "dnspython==1.16.0"
        pip install "Flask==2.0.2"
        pip install "Flask-Cors==3.0.10"
        pip install "gunicorn==20.1.0"
        pip install "iniconfig==1.1.1"
        pip install "itsdangerous==2.0.1"
        pip install "Jinja2==3.0.2"
        pip install "jmespath==1.0.1"
        pip install "MarkupSafe==2.0.1"
        pip install "packaging==21.0"
        pip install "pluggy==1.0.0"
        pip install "py==1.10.0"
        # pip install "pycairo==1.20.1"
        pip install "pycparser==2.20"
        pip install "PyJWT==2.3.0"
        pip install "pymongo==4.0.1"
        pip install "pyparsing==3.0.0"
        pip install "python-dateutil==2.8.2"
        pip install "PyYAML==6.0"
        pip install "s3transfer==0.6.0"
        pip install "six==1.16.0"
        pip install "toml==0.10.2"
        pip install "urllib3==1.26.11"
        pip install "Werkzeug==2.0.2"
        pip install "wheel==0.37.1"

        pip freeze > requirements.txt
    fi
fi
if [ "$1" = "pipfile" ]; then
    deactivate ;
    pipenv lock
fi
if [ "$1" = "deploy" ]; then
    cd ..
    vercel ;
fi
if [ "$1" = "deploy_prod" ]; then
    cd ..
    vercel --prod ;
fi
if [ "$1" = "rename_staging" ]; then
    cd ..
    vercel alias $2 fynapp-staging-tomkat-cr.vercel.app
fi
if [[ "$1" = "" || "$1" = "vercel" ]]; then
    cd ..
    vercel dev --listen 0.0.0.0:${PORT} ;
fi
if [ "$1" = "clean" ]; then
    echo "Cleaning..."
    deactivate ;
    rm -rf __pycache__ ;
    rm -rf bin ;
    rm -rf include ;
    rm -rf instance ;
    rm -rf lib ;
    rm -rf var ;
    rm -rf pyvenv.cfg ;
    rm -rf ../.vercel/cache ;
    rm -rf ../instance ;
    ls -lah 
fi
if [ "$1" = "flask" ]; then
    flask run ;
fi
