#!/bin/sh
# Archivo: "1-run-jfrog-container.sh"
# 2022-03-03 | CR
# Ejecutar con: 
# sh -x 1-run-jfrog-container.sh
# source 1-run-jfrog-container.sh

# Especifica donde esta el script en la maquina local,
# que debe estar en el mismo directorio de este script:
cd "`dirname "$0"`" ;
SCRIPTS_DIR="`pwd`" ;
export CONTAINER_NAME="jfrog_fynapp_backend"

# Credenciales desde un .env (deberian ir mas bien en un "Vault")
cd ${SCRIPTS_DIR}
if [ -f ".env" ]; then
    set -o allexport; . "${SCRIPTS_DIR}/.env"; set +o allexport ;
fi

# Hace que el script de instalación sea ejecutable, para poder ejecutarlo directamente con el "docker run"
if [ -x "$0" ] ;
then
    echo "Script is already executable" ;
else
    echo "A continuacion introduzca la contraseña del usuario 'root' para hacer ejecutable el script de instalación: $0" ;
    sudo chmod +x "$0" ;
fi

if [ "$1" == "build" ] ;
then
    # Si se pasa "build" como 1er parametro, hace el build
    docker-compose build app ;
fi

if [ "$1" == "down" ] ;
then
    # Si se pasa "down" como 1er parametro, baja los contenedores
    docker-compose down ;
else
    # Levanta el container y lo deja corriendo "daemonized":
    docker-compose up -d ;
    # Muestra los contenedores levantados
    docker-compose ps ;
    # Entra en el contenedor
    docker exec -ti ${CONTAINER_NAME} bash
fi

# Muestra lo que esta pasando en el contenedor
#docker attach ${CONTAINER_NAME}

# Entra en el contenedor
#docker exec -ti ${CONTAINER_NAME} bash
