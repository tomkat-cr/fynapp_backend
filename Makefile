# .DEFAULT_GOAL := local
# .PHONY: tests
SHELL := /bin/bash

# General Commands
help:
	cat Makefile

install: cleanLogs
	pipenv install

cleanLogs:
	echo "" > logs/fynapp_general.log

lockedInstall:
	pipenv install --ignore-pipfile

dev:
	pipenv install --dev

lockedDev:
	pipenv install --dev --ignore-pipfile

clean:
	pipenv --rm

fresh: clean install

# Development Commands
tests:
	# pipenv run pytest tests --junitxml=report.xml
	sh scripts/run_fynapp_backend_tests.sh

test: tests

lint:
	pipenv run prospector

types:
	pipenv run mypy .

coverage:
	pipenv run coverage run -m unittest discover tests;
	pipenv run coverage report

format:
	pipenv run yapf -i *.py **/*.py **/**/*.py

format-check:
	pipenv run yapf --diff *.py **/*.py **/**/*.py

qa: lint types tests format-check

# Application Specific Commands
requirements:
	pipenv run pip freeze >> requirements.txt

config:
	# pipenv run chalice_config

deploy: requirements config
	# pipenv run chalice deploy --stage api

local: config cleanLogs
	# saml2aws login -a Mediabros-Dev
	# saml2aws exec -a Mediabros-Dev "pipenv run chalice local --port 8980"
	sh scripts/run_fynapp_backend.sh

server: local

api: config cleanLogs
	# ./scripts/run_local.sh
	sh scripts/run_server.sh
