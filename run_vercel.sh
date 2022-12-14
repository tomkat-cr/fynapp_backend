#!/bin/sh
if [ "$1" = "deactivate" ]; then
    cd fynapp_api ;
    deactivate ;
fi
if [[ "$1" != "deactivate" && "$1" != "pipfile" && "$1" != "clean" ]]; then
    set -o allexport; . "./.env"; set +o allexport ;
    python3 -m venv fynapp_api ;
    . fynapp_api/bin/activate ;
    cd fynapp_api ;
    pip3 install -r requirements.txt ;
fi
if [ "$1" = "pipfile" ]; then
    deactivate ;
    pipenv lock
fi
if [ "$1" = "deploy" ]; then
    vercel ;
fi
if [ "$1" = "deploy_prod" ]; then
    vercel --prod ;
fi
if [[ "$1" = "" || "$1" = "vercel" ]]; then
    vercel dev --listen 0.0.0.0:5001 ;
fi
if [ "$1" = "clean" ]; then
    echo "Cleaning..."
    deactivate ;
    rm -rf __pycache__ ;
    rm -rf bin ;
    rm -rf include ;
    rm -rf lib ;
    rm -rf pyvenv.cfg ;
    ls -lah 
fi
if [ "$1" = "flask" ]; then
    flask run ;
fi
