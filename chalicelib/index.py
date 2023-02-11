import os
import logging
import sys

from flask import Flask
from flask_cors import CORS

from chalicelib.config.config import config
from chalicelib.util.app_logger import log_debug
from chalicelib.models.users import users
from chalicelib.models.food_moments import food_moments


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, support_credentials=True)

    if test_config is None:
        # app.config.from_pyfile('config.py', silent=True)
        app.config.from_object(config.DevelopmentConfig)
    else:
        app.config.from_mapping(test_config)
    app.secret_key = app.config['SECRET_KEY']

    # Ensure the instance folder exists ¿?
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    # Register the BluePrints
    log_debug('>>--> Register the BluePrints...')
    app.register_blueprint(users.bp)
    app.register_blueprint(food_moments.bp)
    log_debug('>>--> BluePrints registered...')

    return app


app = create_app()
