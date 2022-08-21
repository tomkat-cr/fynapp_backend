# FynApp Backend
FynApp is an application to achieve weight loss goals and maintain a better lifestyle, based on proper nutrition, a positive mindset, and physical activity. Inspired by the principles of Caloric Deficit and Intermittent Fasting, the idea was born when one of the founders needed a practical tool to count daily calories with ingredients and recipes made by oneself, raising awareness of the most convenient foods, most filling, the ones you like the most, the ones you can pay for and provide fewer calories, and he didn't found something that fit his needs in the Apps market.
FYN = Fit You Need (Just as Yoda would say).

FynApp es una aplicación para lograr objetivos de reducción de peso y mantener un mejor estilo de vida, con base en alimentación adecuada, mente positiva y actividad física. Inspirada por los principios del Déficit Calórico y el Ayuno Intermitente, la idea nació de contar con una herramienta práctica para hacer un conteo de calorías diarias con ingredientes y recetas hechas por uno mismo, haciendo conciencia de los alimentos que más convienen, que más llenan, que mas le gustan, que puede pagar y que menos calorías aporten.
FYN = Fit You Need (Tal como lo diria el Yoda)

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
2. La URI de las colecciones de Postman usada para el proyecto está en [test/FynApp.postman_collection.json](test/FynApp.postman_collection.json)
3. Importar colección dentro de Postman [Instrucciones](https://learning.getpostman.com/docs/postman/collections/data_formats/#exporting-and-importing-postman-data)

# NOTA:
Normalmente el backend usa el puerto 5001 en localhost.
