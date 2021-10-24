import os


class Config(object):
    DEBUG = True
    SECRET_KEY = 'dev'
    FYNAPP_DB_URI = os.environ['FYNAPP_DB_URI']
    FYNAPP_DB_NAME = os.environ['FYNAPP_DB_NAME']


class DevelopmentConfig(Config):
    DEBUG = False
