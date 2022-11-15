from bson.json_util import dumps, ObjectId

from util.app_logger import log_debug, log_warning
from util.utilities import get_standard_base_exception_msg, current_datetime_timestamp, get_default_resultset
from util.db_helpers import db


# ----------------------- food_moments -----------------------

# Table: food_moments
# PK: _id
# Fields:
#     _id
#     name


def fetch_food_moments_list(skip, limit):
    resultset = get_default_resultset()

    proyeccion = {}
    try:
        resultset['resultset'] = dumps(db.food_moments.find({}, proyeccion).skip(int(skip)).limit(int(limit)))
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FFML1')
        resultset['error'] = True

    return resultset


def fetch_food_moment(food_moments_id):
    resultset = get_default_resultset()

    db_row = fetch_food_moment_raw(food_moments_id)
    if not db_row['resultset']:
        resultset['error_message'] = 'Id {} doesn\'t exist [FFM1].'.format(food_moments_id)
    elif db_row['error']:
        resultset['error_message'] = db_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    try:
        resultset['resultset'] = dumps(db_row['resultset'])
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FFM2')
        resultset['error'] = True

    return resultset


def fetch_food_moment_raw(food_moments_id):
    resultset = get_default_resultset()

    try:
        id = ObjectId(food_moments_id)
    except ValueError:
        resultset['error_message'] = 'Id `{}` is invalid [FFMR1].'.format(food_moments_id)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FFMR2')
        # raise

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    try:
        resultset['resultset'] = db.food_moments.find_one({'_id': id})
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FFMR3')
        resultset['error'] = True

    return resultset


def fetch_food_moment_by_entryname_raw(entry_name, entry_value):
    resultset = get_default_resultset()

    try:
        resultset['resultset'] = db.food_moments.find_one({entry_name: entry_value})
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FFMBEN1')
        resultset['error'] = True

    return resultset


def get_food_moment_id_as_string(food_moment):
    # log_debug( 'get_food_moment_id_as_string) food_moment[]: {}'.format(food_moment) )
    return str(food_moment['_id'])


def create_food_moment(json):
    resultset = get_default_resultset()

    if not 'name' in json:
        resultset['error_message'] = 'error: Name wasn\'t specified [CFM1].'
    else:
        db_row = fetch_food_moment_by_entryname_raw('name', json['name'])
        if db_row['resultset']:
            resultset['error_message'] = 'Food Moment {} already exists [CFM4].'.format(json['name'])
        elif db_row['error']:
            resultset['error_message'] = db_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    json['creation_date'] = json['update_date'] = current_datetime_timestamp()

    try:
        resultset['resultset']['_id'] = str(db.food_moments.insert_one(json).inserted_id)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'CFM5')
        resultset['error'] = True
    else:
        resultset['resultset']['rows_affected'] = '1'

    return resultset


def update_food_moments(record):
    resultset = get_default_resultset()

    mandatory_elements = {
        'name',
    }
    updated_record = dict(record)
    resultset['error_message'] = ''
    for element in mandatory_elements:
        if(element not in record):
            resultset['error_message'] = '{}{}{}'.format(
                resultset['error_message'],
                ', ' if resultset['error_message'] != '' else '',
                element
            )

    if resultset['error_message']:
        resultset['error_message'] = 'Missing mandatory elements: {} [UFM1].'.format(resultset['error_message'])
        resultset['error'] = True
        return resultset

    updated_record['update_date'] = current_datetime_timestamp()

    if '_id' not in record and 'id' in record:
        record['_id'] = record['id']
        del record['id']

    if '_id' in updated_record:
        # To avoid "WriteError('Performing an update on the path '_id' would modify the immutable field '_id'
        del updated_record['_id']

    try:
        resultset['resultset']['rows_affected'] = str(db.food_moments.update_one({'_id': ObjectId(record['_id'])}, {
            '$set': updated_record
        }).modified_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'UFM2')
        resultset['error'] = True

    return resultset


def delete_food_moment(food_moment_id):
    resultset = get_default_resultset()

    db_row = fetch_food_moment_by_entryname_raw('_id', ObjectId(food_moment_id))
    if not db_row['resultset']:
        resultset['error_message'] = 'error: Food Moment {} doesn\'t exist [DFM1].'.format(food_moment_id)
    elif db_row['error']:
        resultset['error_message'] = db_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    try:
        resultset['resultset']['rows_affected'] = str(db.food_moments.delete_one({'_id': ObjectId(food_moment_id)}).deleted_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'DFM2')
        resultset['error'] = True

    return resultset
