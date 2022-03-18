from flask import Blueprint, request, current_app
from flask_cors import cross_origin
import json

from . import db
from fynapp_api.util import db_helpers
from fynapp_api.util.app_logger import log_debug
from fynapp_api.util.jwt import token_required, token_encode
from fynapp_api.util.passwords import verify_password, encrypt_password
from fynapp_api.util.utilities import return_resultset_jsonified_or_exception, get_default_resultset


bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
@cross_origin(supports_credentials=True)
def users_func():

    user_id = request.args.get('id')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    request_body = request.get_json()

    if request.method == 'POST':
        # Crear user
        log_debug( 'CU-1) CREATE user | request_body: {}'.format(request_body) )
        result = db.create_user(request_body)
        log_debug( 'CU-2) Create user | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif request.method == 'PUT':
        # Actualizar datos del user
        log_debug( 'UU-1) UPDATE user | request_body: {}'.format(request_body) )
        result = db.update_users(request_body)
        log_debug( 'UU-2) Update user | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif request.method == 'DELETE' and user_id is not None:
        # Borrar un user usando el _id
        log_debug( 'DU-1) DELETE user | user_id: {}'.format(user_id) )
        result = db.delete_user(user_id)
        log_debug( 'DU-2) Delete user | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif user_id is not None:
        # Obtener users por _id
        log_debug( 'GO-1) user by id: {}'.format(user_id) )
        result = db.fetch_user(user_id)
        log_debug( 'GO-2) user by id: {} | result: {}'.format(user_id, result) )
        return return_resultset_jsonified_or_exception(result)

    else:
        # Obtener lista de users
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        log_debug( 'GA-1) users list | skip: {} | limit: {}'.format(skip, limit) )
        result = db.fetch_users_list(skip, limit)
        log_debug( 'GA-2) users list | result {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)


@bp.route('/user-food-times', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
@cross_origin(supports_credentials=True)
def add_food_times():
    user_id = request.args.get('user_id')
    food_moment_id = request.args.get('food_moment_id')
    food_time = request.args.get('food_time')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    request_body = request.get_json()
    filters = {}
    if food_moment_id != None:
        filters['food_moment_id'] = food_moment_id
    if food_time != None:
        filters['food_time'] = food_time

    # Create
    if request.method == 'POST':

        log_debug( '>>> add_food_times | PUT request_body = {}'.format(request_body) )
        return return_resultset_jsonified_or_exception(db.add_food_times_to_user(request_body))
    
    # Delete
    if request.method == 'DELETE':

        log_debug( '>>> add_food_times | DELETE request_body = {}'.format(request_body) )
        return return_resultset_jsonified_or_exception(db.remove_food_times_to_user(request_body))

    # List
    if request.method == 'GET':

        # Get the list (paginated) or one especific element
        return return_resultset_jsonified_or_exception(db.fetch_user_food_times(user_id, filters, skip, limit))

    # Modify
    if request.method == 'PUT':

        # When one element needs to bee modified, first remove it, then add it again
        log_debug( '>>> add_food_times | POST request_body = {}'.format(request_body) )
        remove_operation_result = db.remove_food_times_to_user(request_body)
        if remove_operation_result['error']:
            return return_resultset_jsonified_or_exception(remove_operation_result)
        return return_resultset_jsonified_or_exception(db.add_food_times_to_user(request_body))


@bp.route('/user-user-history', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
@cross_origin(supports_credentials=True)
def add_user_history():
    request_body = request.get_json()
    if request.method == 'PUT':
        return return_resultset_jsonified_or_exception(db.add_user_history_to_user(request_body))
    elif request.method == 'DELETE':
        return return_resultset_jsonified_or_exception(db.remove_user_history_to_user(request_body))


@bp.route('/test')
@token_required
@cross_origin(supports_credentials=True)
def test_connection():
    result = get_default_resultset()
    result['resultset']['collections'] = json.loads(db_helpers.test_connection())
    return return_resultset_jsonified_or_exception(result)


@bp.route('/login', methods=['GET', 'POST'])  
@cross_origin(supports_credentials=True)
def login_user(): 
    result = get_default_resultset()

    auth = request.authorization
    # log_debug( 'login_user | request: {}'.format(request) )
    # log_debug( 'login_user | auth: {}'.format(auth) )
    if not auth or not auth.username or not auth.password:  
        result['error_message'] = 'could not verify [L1]'
        return return_resultset_jsonified_or_exception(result)

    user = db.fetch_user_by_entryname_raw('email', auth.username)
    if user['error']:
        return return_resultset_jsonified_or_exception(user)

    # log_debug( 'login_user | user[resultset]: {}'.format(user) )

    if user['resultset']:
        if verify_password(user['resultset']['passcode'], auth.password):  
            token = token_encode(user['resultset'])
            result['resultset'] = {
                'token' : token,
                '_id': db.get_user_id_as_string(user['resultset']),
                'firstname': user['resultset']['firstname'],
                'lastname': user['resultset']['lastname'],
                'email': user['resultset']['email'],
                'username': user['resultset']['email'],
            }
        else:
            result['error_message'] = 'could not verify [L3]'
    else:
        result['error_message'] = 'could not verify [L2]'

    log_debug( 'login_user | FINAL result: {}'.format(result) )

    return return_resultset_jsonified_or_exception(result)


@bp.route('/pas-enc', methods=['POST'])
@token_required
@cross_origin(supports_credentials=True)
def password_encripted():
    request_body = request.get_json()
    result = get_default_resultset()
    result['resultset'] = {}
    if request_body.get('passwd', None) != None:
        result['resultset'] = {
            # 'orig_pass': request_body.get('passwd'),
            'enc_pass': encrypt_password(request_body.get('passwd'))
        }
    else:
        result['error_message'] = 'Parameter not received [PSEN1]'
    return return_resultset_jsonified_or_exception(result)


@bp.route('/supad-create', methods=['POST'])  
def super_admin_create():
    result = get_default_resultset()

    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        result['error_message'] = 'could not verify [SAC1]'
    elif auth.username != current_app.config['FYNAPP_SUPERADMIN_EMAIL']:
        result['error_message'] = 'could not verify [SAC2]'
    elif not verify_password(encrypt_password(current_app.config['FYNAPP_SECRET_KEY']), auth.password):
        result['error_message'] = 'could not verify [SAC3]'

    if result['error_message']:
        return return_resultset_jsonified_or_exception(result)

    user = db.fetch_user_by_entryname_raw('email', auth.username)
    if user['error']:
        return return_resultset_jsonified_or_exception(user)

    if user['resultset']:
        result['error_message'] = 'User already exists [SAC4]'
    else:
        request_body = {
            "firstname": "Admin",
            "lastname": "Super",
            "superuser": "1",
            'email': auth.username,
            'passcode': auth.password,
            "creation_date": 1635033994,
            "update_date": 1635033994,
            "birthday": -131760000,
            "height": "1.70",
            "height_unit": "m",
            "weight": "76.0",
            "weight_unit": "kg",
            "training_days": "MTWXFS",
            "training_hour": "17:00",
            # "eating_hours": "{'BF':'07:00', 'MMS':'09:00', 'LU':'12:00', 'MAS':'15:00', 'DI':'18:00'}"
        }
        result = db.create_user(request_body)

    return return_resultset_jsonified_or_exception(result)
