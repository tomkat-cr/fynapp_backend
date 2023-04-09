# from bson.json_util import dumps
from flask import current_app

from flask import request
# import uuid
import jwt
import datetime
from functools import wraps

# from util.app_logger import log_debug, log_warning
from .utilities import standard_error_return
from fynapp_api.models.users.db import get_user_id_as_string


# ----------------------- JWT -----------------------

# HEADER_TOKEN_ENTRY_NAME = 'x-access-tokens'
HEADER_TOKEN_ENTRY_NAME = 'Authorization'
EXPIRATION_MINUTES = 30


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # log_debug(
        #   'token_required | request.headers: {}'.format(request.headers)
        # )
        if HEADER_TOKEN_ENTRY_NAME in request.headers:
            token = request.headers[HEADER_TOKEN_ENTRY_NAME]
            token = token.replace('Bearer ', '')
        if not token:
            return standard_error_return('a valid token is missing')
        # log_debug(
        #   'la clave: {}'.format(current_app.config['FYNAPP_SECRET_KEY'])
        # )
        # log_debug('el token: {}'.format(token))
        try:
            data = jwt.decode(
                token,
                current_app.config['FYNAPP_SECRET_KEY'],
                algorithms="HS256"
            )
            # current_user = fetch_user_raw(users_id=data['public_id'])
        except Exception:
            return standard_error_return('token is invalid')
        # return f(current_user, *args, **kwargs)
        return f(*args, **kwargs)
    return decorator


def token_encode(user):
    token = jwt.encode(
        {
            'public_id': get_user_id_as_string(user),
            'exp': 
                datetime.datetime.utcnow() + 
                datetime.timedelta(minutes=EXPIRATION_MINUTES)
        },
        current_app.config['FYNAPP_SECRET_KEY'],
        algorithm="HS256"
    )
    return token
