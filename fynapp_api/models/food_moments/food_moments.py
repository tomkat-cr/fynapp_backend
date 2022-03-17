from flask import Blueprint, request, current_app
from flask_cors import cross_origin
import json

from . import db
from fynapp_api.util.app_logger import log_debug
from fynapp_api.util.jwt import token_required, token_encode
from fynapp_api.util.utilities import return_resultset_jsonified_or_exception, get_default_resultset


bp = Blueprint('food_moments', __name__, url_prefix='/food_moments')


@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
@cross_origin(supports_credentials=True)
def food_moments_func():

    food_moment_id = request.args.get('id')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    request_body = request.get_json()

    if request.method == 'POST':
        # Crear food_moment
        log_debug( 'CU-1) CREATE food_moment | request_body: {}'.format(request_body) )
        result = db.create_food_moment(request_body)
        log_debug( 'CU-2) Create food_moment | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif request.method == 'PUT':
        # Actualizar datos del food_moment
        log_debug( 'UU-1) UPDATE food_moment | request_body: {}'.format(request_body) )
        result = db.update_food_moments(request_body)
        log_debug( 'UU-2) Update food_moment | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif request.method == 'DELETE' and food_moment_id is not None:
        # Borrar un food_moment usando el _id
        log_debug( 'DU-1) DELETE food_moment | food_moment_id: {}'.format(food_moment_id) )
        result = db.delete_food_moment(food_moment_id)
        log_debug( 'DU-2) Delete food_moment | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif food_moment_id is not None:
        # Obtener food_moments por _id
        log_debug( 'GO-1) food_moment by id: {}'.format(food_moment_id) )
        result = db.fetch_food_moment(food_moment_id)
        log_debug( 'GO-2) food_moment by id: {} | result: {}'.format(food_moment_id, result) )
        return return_resultset_jsonified_or_exception(result)

    else:
        # Obtener lista de food_moments
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        log_debug( 'GA-1) food_moments list | skip: {} | limit: {}'.format(skip, limit) )
        result = db.fetch_food_moments_list(skip, limit)
        log_debug( 'GA-2) food_moments list | result {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)
