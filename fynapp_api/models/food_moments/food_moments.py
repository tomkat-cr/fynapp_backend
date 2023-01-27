from flask import Blueprint, request
from flask_cors import cross_origin

from . import db
from fynapp_api.util.app_logger import log_debug
from fynapp_api.util.jwt import token_required
from fynapp_api.util.utilities import return_resultset_jsonified_or_exception


bp = Blueprint('food_moments', __name__, url_prefix='/food_moments')


@bp.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_required
@cross_origin(supports_credentials=True)
def food_moments_crud():

    food_moment_id = request.args.get('id')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    request_body = request.get_json()

    if request.method == 'POST':
        # Create a food_moment / Crear un food_moment
        log_debug( 'CFM-1) CREATE food_moment | request_body: {}'.format(request_body) )
        result = db.create_food_moment(request_body)
        log_debug( 'CFM-2) Create food_moment | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif request.method == 'PUT':
        # Update one food_moment by _id / Actualizar datos del food_moment
        log_debug( 'UFM-1) UPDATE food_moment | request_body: {}'.format(request_body) )
        result = db.update_food_moments(request_body)
        log_debug( 'UFM-2) Update food_moment | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif request.method == 'DELETE' and food_moment_id is not None:
        # Delete one food_moment by _id / Borrar un food_moment usando el _id
        log_debug( 'DFM-1) DELETE food_moment | food_moment_id: {}'.format(food_moment_id) )
        result = db.delete_food_moment(food_moment_id)
        log_debug( 'DFM-2) Delete food_moment | result: {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)

    elif food_moment_id is not None:
        # Fetch one food_moment data by _id / Obtener food_moments por _id
        log_debug( 'GFM-1) food_moment by id: {}'.format(food_moment_id) )
        result = db.fetch_food_moment(food_moment_id)
        log_debug( 'GFM-2) food_moment by id: {} | result: {}'.format(food_moment_id, result) )
        return return_resultset_jsonified_or_exception(result)

    else:
        # Fetch food_moment list / Obtener lista de food_moments
        skip = (skip, 0)[skip is None]
        limit = (limit, 10)[limit is None]
        log_debug( 'GLFM-1) food_moments list | skip: {} | limit: {}'.format(skip, limit) )
        result = db.fetch_food_moments_list(skip, limit)
        log_debug( 'GLFM-2) food_moments list | result {}'.format(result) )
        return return_resultset_jsonified_or_exception(result)
