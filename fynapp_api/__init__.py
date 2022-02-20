import os
import logging
import sys

from flask import Flask
from flask_cors import CORS, cross_origin
from . import config

from .models import users
from fynapp_api.util.app_logger import log_debug, log_warning


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, support_credentials=True)

    if test_config is None:
        # app.config.from_pyfile('config.py', silent=True)
        app.config.from_object(config.DevelopmentConfig)
    else:
        app.config.from_mapping(test_config)
    app.secret_key = app.config['FYNAPP_SECRET_KEY']

    # Ensure the instance folder exists ¿?
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    # Register the BluePrints
    log_debug( '>>--> Register the BluePrints...' )
    app.register_blueprint(users.bp)
    log_debug( '>>--> BluePrints registered...' )

    return app
