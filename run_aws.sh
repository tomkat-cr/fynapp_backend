#!/bin/sh
# run_aws.sh
# 2023-02-02 | CR
#
APP_DIR='chalicelib'
PYTHON3_EXEC='/usr/local/bin/python3.9'
AWS_STACK_NAME='fynapp-be-stack'
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

if [ "$1" = "pipfile" ]; then
    deactivate ;
    
    pipenv --python 3.9

    pipenv install "attrs==21.2.0"
    pipenv install "certifi==2018.11.29"
    pipenv install "cffi==1.15.0"
    pipenv install "click==8.0.3"
    pipenv install "cryptography==35.0.0"
    pipenv install "dnspython==1.16.0"
    pipenv install "iniconfig==1.1.1"
    pipenv install "itsdangerous==2.0.1"
    pipenv install "Jinja2==3.0.2"
    pipenv install "jmespath==1.0.1"
    pipenv install "MarkupSafe==2.0.1"
    pipenv install "packaging==21.0"
    pipenv install "pluggy==1.0.0"
    pipenv install "py==1.10.0"
    # pipenv install "pycairo==1.20.1"
    pipenv install "pycparser==2.20"
    pipenv install "PyJWT==2.3.0"
    pipenv install "pyparsing==3.0.0"
    pipenv install "python-dateutil==2.8.2"
    pipenv install "PyYAML==6.0"
    pipenv install "s3transfer==0.6.0"
    pipenv install "six==1.16.0"
    pipenv install "toml==0.10.2"
    pipenv install "urllib3==1.26.11"
    pipenv install "wheel==0.37.1"

    # Flask
    # pipenv install "Flask==2.0.2"
    # pipenv install "Flask-Cors==3.0.10"
    # pipenv install "gunicorn==20.1.0"

    # FasAPI
    # pipenv install fastapi
    # pipenv install a2wsgi
    
    # Mongo
    pipenv install "pymongo==4.0.1"
    pipenv install "Werkzeug==2.0.2"

    # AWS
    # pipenv install boto3
    pipenv install "boto3==1.24.55"
    pipenv install "botocore==1.27.55"
    pipenv install chalice

    pipenv lock
    pipenv requirements > requirements.txt
fi

if [ "$1" = "clean" ]; then
    echo "Cleaning..."
    cd ${APP_DIR} ;
    deactivate ;
    rm -rf __pycache__ ;
    rm -rf ../__pycache__ ;
    rm -rf bin ;
    rm -rf include ;
    rm -rf lib ;
    rm -rf src ;
    rm -rf pyvenv.cfg ;
    rm -rf .vercel/cache ;
    rm -rf ../.vercel/cache ;
    rm -rf ../node_modules ;
    rm requirements.txt
    ls -lah
fi

if [[ "$1" = "test" ]]; then
    # echo "Error: no test specified" && exit 1
    echo "Run test..."
    python -m pytest
    echo "Done..."
fi

if [[ "$1" = "run" || "$1" = "" ]]; then
    pipenv shell chalice local --port ${PORT}
    exit
fi

if [ "$1" = "deploy" ]; then
    pipenv requirements > requirements.txt
    pipenv shell chalice deploy --stage dev
    exit
fi
if [ "$1" = "deploy_prod" ]; then
    pipenv requirements > requirements.txt
    pipenv shell chalice deploy --stage prod
    exit
fi

if [ "$1" = "create_stack" ]; then
    aws cloudformation deploy --template-file "${APP_DIR}/.chalice/dynamodb_cf_template.yaml" --stack-name "${AWS_STACK_NAME}"
    # aws cloudformation describe-stack-events --stack-name "${AWS_STACK_NAME}"
fi

if [ "$1" = "delete_app" ]; then
    # Delete application
    pipenv shell chalice delete
    exit
fi

if [ "$1" = "delete_stack" ]; then
    # Delete DynamoDb table
    aws cloudformation delete-stack --stack-name "${AWS_STACK_NAME}"
fi
