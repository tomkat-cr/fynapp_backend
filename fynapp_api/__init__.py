import os

from flask import Flask
from flask_cors import CORS, cross_origin
from . import config

from .models import users


def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, support_credentials=True)

    if test_config is None:
        # app.config.from_pyfile('config.py', silent=True)
        app.config.from_object(config.DevelopmentConfig)
    else:
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists ¿?
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register the BluePrints
    app.register_blueprint(users.bp)

    return app
