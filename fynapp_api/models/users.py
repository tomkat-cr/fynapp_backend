from flask import Blueprint, request, jsonify, make_response, current_app
from flask_cors import CORS, cross_origin
from . import db
import json
from fynapp_api.util.app_logger import log_debug, log_warning
from fynapp_api.util.utilities import standard_error_return

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
@db.token_required
@cross_origin(supports_credentials=True)
def users_func():
    user_id = request.args.get('id')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    request_body = request.get_json()
    if request.method == 'POST':
        # Crear user
        result = db.create_user(request_body)
        if result.startswith('error:'):
            return jsonify({'error': result})
        return jsonify({'_id': result})
    elif request.method == 'PUT':
        # Actualizar datos del user
        result = db.update_users(request_body)
        if result.startswith('error:'):
            return jsonify({'error': result})
        return jsonify({'updates': result})
    elif request.method == 'DELETE' and user_id is not None:
        # Borrar un user usando el _id
        result = db.delete_user(user_id)
        if result.startswith('error:'):
            return jsonify({'error': result})
        return jsonify({'deletions': result})
    elif user_id is not None:
        # Obtener users por _id
        result = db.fetch_user(user_id)
        if 'error' in result:
            return jsonify(result)
        return jsonify({'user': json.loads(result)})
    else:
        # Obtener users
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        result = db.fetch_users_list(skip, limit)
        log_warning( 'users list | result {}'.format(result) )
        if 'error' in result:
            # return jsonify(result)
            log_warning( 'users list ERROR | result.message {}'.format(result.message) )
            return standard_error_return(result.message)
        return jsonify({'users': json.loads(result)})


@bp.route('/add-food-times-to-user', methods=['PUT', 'DELETE'])
@db.token_required
@cross_origin(supports_credentials=True)
def add_food_times():
    request_body = request.get_json()
    if request.method == 'PUT':
        return jsonify({'updates': db.add_food_times_to_user(request_body)})
    elif request.method == 'DELETE':
        return jsonify({'deletions': db.remove_food_times_to_user(request_body)})


@bp.route('/add-user-history-to-user', methods=['PUT', 'DELETE'])
@db.token_required
@cross_origin(supports_credentials=True)
def add_user_history():
    request_body = request.get_json()
    if request.method == 'PUT':
        return jsonify({'updates': db.add_user_history_to_user(request_body)})
    elif request.method == 'DELETE':
        return jsonify({'deletions': db.remove_user_history_to_user(request_body)})


@bp.route('/test')
@db.token_required
@cross_origin(supports_credentials=True)
def test_connection():
    return jsonify({'collections': json.loads(db.test_connection())})


@bp.route('/login', methods=['GET', 'POST'])  
@cross_origin(supports_credentials=True)
def login_user(): 
    auth = request.authorization
    # log_warning( 'login_user | request: {}'.format(request) )
    # log_warning( 'login_user | auth: {}'.format(auth) )
    headers = {'WWW.Authentication': 'Basic realm: "login required"'}
    errorcode = 401
    if not auth or not auth.username or not auth.password:  
        return standard_error_return('could not verify [L1]')
    user = db.fetch_user_by_entryname_raw('email', auth.username)
    if user:
        if db.verify_password(user['passcode'], auth.password):  
            token = db.token_encode(user)
            # return jsonify({'token' : token.decode('UTF-8')})
            return jsonify({
                'token' : token,
                '_id': db.get_user_id_as_string(user),
                'firstname': user['firstname'],
                'lastname': user['lastname'],
                'email': user['email'],
                'username': user['email'],
            })
        else:
            return standard_error_return('could not verify [L3]')
    else:
        return standard_error_return('could not verify [L2]')


@bp.route('/supad-create', methods=['POST'])  
def super_admin_create():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return standard_error_return('could not verify [SAC1]')
    if auth.username != current_app.config['FYNAPP_SUPERADMIN_EMAIL']:
        return standard_error_return('could not verify [SAC2]')
    if not db.verify_password(db.encrypt_password(current_app.config['FYNAPP_SECRET_KEY']), auth.password):
        return standard_error_return('could not verify [SAC3]')
    user = db.fetch_user_by_entryname_raw('email', auth.username)
    if user:
        return standard_error_return('User already exists [SAC4]')
    else:
        request_body = {
            "firstname": "Admin",
            "lastname": "Super",
            "superuser": "1",
            'email': auth.username,
            'passcode': auth.password,
            "creation_date": 1635033994,
            "birthday": -131760000,
            "height": "76.0",
            "tall": "1.70",
            "height_unit": "kg",
            "tall_unit": "meters",
            "training_days": "MTWXFS",
            "training_hour": "17:00"
        }
        return jsonify({'_id': db.create_user(request_body)})
