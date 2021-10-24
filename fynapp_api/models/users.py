from flask import Blueprint, request, jsonify
from . import db
import json

bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
def users_func():
    user_id = request.args.get('id')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    request_body = request.get_json()
    if request.method == 'POST':
        # Crear user
        return jsonify({'_id': db.create_user(request_body)})
    elif request.method == 'PUT':
        # Actualizar datos del user
        return jsonify({'updates': db.update_users(request_body)})
    elif request.method == 'DELETE' and user_id is not None:
        # Borrar un user usando el _id
        return jsonify({'deletions': db.delete_user(user_id)})
    elif user_id is not None:
        # Obtener users por _id
        result = db.fetch_user(user_id)
        return jsonify({'user': json.loads(result)})
    else:
        # Obtener users
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        result = db.fetch_users_list(skip, limit)
        return jsonify({'users': json.loads(result)})


@bp.route('/add-food-times-to-user', methods=['PUT', 'DELETE'])
def add_food_times():
    request_body = request.get_json()
    if request.method == 'PUT':
        return jsonify({'updates': db.add_food_times_to_user(request_body)})
    elif request.method == 'DELETE':
        return jsonify({'deletions': db.remove_food_times_to_user(request_body)})


@bp.route('/add-user-history-to-user', methods=['PUT', 'DELETE'])
def add_user_history():
    request_body = request.get_json()
    if request.method == 'PUT':
        return jsonify({'updates': db.add_user_history_to_user(request_body)})
    elif request.method == 'DELETE':
        return jsonify({'deletions': db.remove_user_history_to_user(request_body)})


@bp.route('/test')
def test_connection():
    return jsonify({'collections': json.loads(db.test_connection())})
