from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app


# ----- passwords


def encrypt_password(passcode):
    # return generate_password_hash(passcode, method='sha256')
    return generate_password_hash(current_app.config['FYNAPP_SECRET_KEY']+passcode, method='sha256')


def verify_password(db_user_password, form_auth_password):
    # return check_password_hash(user_password, auth_password)
    return check_password_hash(db_user_password, current_app.config['FYNAPP_SECRET_KEY']+form_auth_password)
