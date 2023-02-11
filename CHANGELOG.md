# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).


## Unreleased
---

### New

### Changes

### Fixes

### Breaks


## 0.1.6 (2023-02-10)
---

### New
"verify_required_fields" function introduced to have a unified and normalized way to verify mandatory fields.
".env-example" introduced.

### Changes
FA-67 - "fynapp_api" directory renamed to "chalicelib" to prepare AWS migration.
"models/dynamodb_table_structures.py" separated to isolate specific dynamoDb table specs from "util/db_helpers.py"
"logs" directory removed.

### Fixes
Default value for FYNAPP_SUPERADMIN_EMAIL removed.
Began Flake8 code formatting fixes.
"from ." replaced by a "from chalicelib." to avoid "ImportError: attempted relative import with no known parent package" error.


## 0.1.5 (2022-11-14)
---

### New
Fix: deploy to vercel as serverless backend


## 0.1.4 (2022-08-21)
---

### New
Add: DynamoDb create table/find_one functionality
applying factory method design pattern


## 0.1.3 (2022-03-19)
---

### Fixes
Fix the user_history CRUD the be compatible and usable as food_moments. food_times_crud and user_history_crud are more generic because now uses variables for the array elements names. FA-6


## 0.1.2 (2022-03-16)
---

### Fixes
FA-24: Fix error No such file or directory: '/app/logs/fynapp_general.log' on Heroku production.
Fix when retrieve food_times from a user row doesn't have it.
FA-6: Fix the bash script to run test to read .env.

### Changes
FA-58: "restart: unless-stopped" to the VPS docker compose configuration, to let the containers stay active on server reboots.
FA-31: Separate databases for prod, staging and development.
FA-51: pull jwt, passwords, token, etc, from db.py to individual files on utilities directory.
FA-6: Create endpoints and unit test for food_moments, and fix the unit test for Users to handle the API results standarization with the `resultset` elements.
Change `tall` and `tall_unit` with `weight` and `weight_unit`
Fix the user_history CRUD the be compatible and usable as food_moments.
food_times_crud and user_history_crud are more generic because now uses variables for the array elements names.
FA-56: Add the fynapp_secret_key to the password hash + an endpoint to get a hashed password.
FA-57: Create scripts to backup and restore mongo databases.
Update `CHANGELOG.md` and `version.txt` files.

### New
FA-33: Editor FE: add child listing to the edit screen.


## 0.1.11 (2022-03-10)
---

### New
Preview version with initial deployment of BE (Backend) and FE (Frontend) of Fynapp webapp.
Implements FA-1, FA-2, FA-3, FA-13, FA-14, FA-15, FA-16, FA-17, FA-18, FA-21, FA-22, FA-23.
Release notes:
Start programming of the generic editor.
FA-1: Start the unit test development with the Users table.
FA-2: Endpoint for Users table.
FA-3: Create a pipeline to build and deploy the backend to a docker container in a Linux VPS.
FA-13: Create a develop branch and start using it with good SDLC practices.
FA-14: Add JWT bearer security to the backend.
FA-15: Create endpoints and unit test for user login.
FA-16: Start FE development by implementing login page and JWT bearer/token.
FA-17: Create CRUD for users on the FE. Enhanced and extended top menu, Users list with bootstrap and fontawesome, initial CRUD layout.
FA-18: Create a pipeline to build and deploy BE & FE on Heroku.
FA-21: Recover local I5 y/o Celeron server and install Centos 7.
FA-22: Install and configure Kubernetes on the local server and perform a spike the evaluate using this technology.
FA-23: Build a docker image in a Gitlab pipeline by install a Gitlab runner.
