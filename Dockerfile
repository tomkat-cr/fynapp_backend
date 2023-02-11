# File: fynapp_backend/Dockerfile
# 2022-02-25 | CR

FROM python:3.9

ARG FLASK_APP=chalicelib
ARG FLASK_ENV=chalicelib
ARG FLASK_DEBUG=0
ARG FYNAPP_DB_NAME=fynapp_dev
ARG FYNAPP_DB_URI
ARG FYNAPP_SECRET_KEY

# Create app directory
WORKDIR /usr/src/app
 
COPY . .

# RUN ls -la

RUN sh -x ./scripts/docker_install_deps.sh
# RUN mkdir ./logs
# RUN echo "" > ./logs/fynapp_general.log
RUN pipenv install --deploy --system

EXPOSE 5000

CMD [ "bash", "scripts/run_server.sh" ]

