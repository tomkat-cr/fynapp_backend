# .DEFAULT_GOAL := local
# .PHONY: tests
SHELL := /bin/bash

# General Commands
help:
	cat Makefile

install: cleanLogs
	pipenv install

cleanLogs:
	sh scripts/clean_logs.sh

lockedInstall:
	pipenv install --ignore-pipfile

dev:
	pipenv install --dev

lockedDev:
	pipenv install --dev --ignore-pipfile

clean:
	pipenv --rm

fresh: clean install

# CLI Utilities
lsof:
	sh scripts/run_lsof.sh

create_aws_config:
	sh scripts/aws/create_aws_config.sh

# Development Commands
tests:
	pipenv run pytest tests --junitxml=report.xml

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
	pipenv run chalice deploy --stage api

local: config cleanLogs
	# saml2aws login -a Mediabros-Dev
	# saml2aws exec -a Mediabros-Dev "pipenv run chalice local --port 8980"
	# ./scripts/run_local.sh
	sh run_aws.sh

server: local

api: config cleanLogs
	# sh scripts/run_server.sh
	sh run_aws.sh
