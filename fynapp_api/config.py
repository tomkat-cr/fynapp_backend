import os


class Config(object):
    DEBUG = True
    SECRET_KEY = 'dev'
    FYNAPP_DB_URI = os.environ['FYNAPP_DB_URI']
    FYNAPP_DB_NAME = os.environ['FYNAPP_DB_NAME']
    FYNAPP_SECRET_KEY = os.environ['FYNAPP_SECRET_KEY']
    FYNAPP_SUPERADMIN_EMAIL = os.environ.get('FYNAPP_SUPERADMIN_EMAIL', 'super@fynapp.com')

class DevelopmentConfig(Config):
    DEBUG = False
