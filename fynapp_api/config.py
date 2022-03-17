import os


class Config(object):
    DEBUG = (os.environ.get('FLASK_DEBUG', '0') == '1')
    SECRET_KEY = os.environ.get('SECRET_KEY', print(os.urandom(16)))
    FYNAPP_DB_URI = os.environ['FYNAPP_DB_URI']
    FYNAPP_DB_NAME = os.environ['FYNAPP_DB_NAME']
    FYNAPP_SECRET_KEY = os.environ['FYNAPP_SECRET_KEY']
    FYNAPP_SUPERADMIN_EMAIL = os.environ.get('FYNAPP_SUPERADMIN_EMAIL', 'super@fynapp.com')

class DevelopmentConfig(Config):
    DEBUG = (os.environ.get('FLASK_DEBUG', '1') == '1')
