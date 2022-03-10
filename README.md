# FynApp Backend
FynApp es una aplicación de gestión para lograr objetivos de alimentación adecuada y mantener un mejor estilo de vida basada en constante actividad física.
2021-10-16 | CR

## Iniciar el sistema
```
export DEV_BASE_DIR="your_base_development_directory_path"
source ${DEV_BASE_DIR}/fynapp_backend/run_fynapp_backend.sh
```

## Ejecutar los test unitatios
```
source ${DEV_BASE_DIR}/fynapp_backend/run_fynapp_backend.sh test
```

## Instalar dependenias del proyecto
Con el ambiente activado, instalar las dependencias:
```
pip install -r requirements.txt
```

## Variables de entorno necesarias para ejecutar el proyecto
Asegurate de reemplazar el valor de FYNAPP_DB_URI por la URI de tu cluster en MongoDB Atlas
Para los ambientes de produccion, estas variables se deben asignar en un archivo .env
```
export FYNAPP_SECRET_KEY="secret"
export FLASK_APP="fynapp_api"
export FLASK_ENV="development"
export FYNAPP_DB_ENV="dev"
export FYNAPP_DB_SERVER="xxxxxxx"
export FYNAPP_DB_NAME="fynapp_${FYNAPP_DB_ENV}"
export FYNAPP_DB_URI="mongodb+srv://${FYNAPP_DB_USR_NAME}:${FYNAPP_DB_USR_PSW}@${FYNAPP_DB_SERVER}"
```

## Iniciar el servidor de fynapp_backend
```
flask run
```
# Postman
1. Descargar e instalar [Postman](https://www.getpostman.com/downloads/)
2. La URI de las colecciones de Postman usada para el proyecto está en [fynapp_backend/FynApp.postman_collection.json](https://gitlab.com/tomkat-cr/fynapp_backend/-/raw/main/postman_collection.json)
3. Importar colección dentro de Postman [Instrucciones](https://learning.getpostman.com/docs/postman/collections/data_formats/#exporting-and-importing-postman-data)

# NOTA:
Normalmente el backend usa el puerto 5000.