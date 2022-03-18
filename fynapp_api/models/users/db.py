from bson.json_util import dumps, ObjectId
from itertools import islice

from fynapp_api.util.app_logger import log_debug, log_warning
from fynapp_api.util.utilities import check_email, standard_error_return, get_standard_base_exception_msg, current_datetime_timestamp, get_default_resultset
from fynapp_api.util.db_helpers import db
from fynapp_api.util.passwords import encrypt_password

# ...
# ...
# ...

# ----------------------- users -----------------------

# Table: users
# PK: _id
# Fields:
#     _id
#     firstname
#     lastname
#     superuser
#     email
#     passcode
#     birthday
#     height
#     height_unit
#     weight
#     weight_unit
#     tall
#     tall_unit
#     training_days
#     training_hour
#     eating_hours
#     creation_date
#     update_date

#     user_history: 
#       [
#           {
#               date
#               goals
#               weight
#               weight_unit
#           }
#       ]
#     food_times:
#       [
#           {
#               food_moment_id -> food_moments._id
#               food_time
#           }
#       ]

    # try:
    # except BaseException as err:
    #     resultset['error_message'] = get_standard_base_exception_msg(err, 'XX')
    #     resultset['error'] = True


def fetch_users_list(skip, limit):
    resultset = get_default_resultset()

    proyeccion = {'passcode': 0}
    try:
        resultset['resultset'] = dumps(db.users.find({}, proyeccion).skip(int(skip)).limit(int(limit)))
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FUL1')
        resultset['error'] = True

    return resultset


def fetch_user(users_id, proyeccion = {}):
    resultset = get_default_resultset()

    db_row = fetch_user_raw(users_id, proyeccion)
    if not db_row['resultset']:
        resultset['error_message'] = 'Id {} doesn\'t exist [FU1].'.format(users_id)
    elif db_row['error']:
        resultset['error_message'] = db_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    try:
        resultset['resultset'] = dumps(db_row['resultset'])
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FU2')
        resultset['error'] = True

    return resultset


def fetch_user_raw(users_id, proyeccion = {}):
    resultset = get_default_resultset()

    try:
        id = ObjectId(users_id)
    except ValueError:
        resultset['error_message'] = 'Id `{}` is invalid [FUR1].'.format(users_id)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FUR2')
        # raise

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    try:
        resultset['resultset'] = db.users.find_one({'_id': id}, proyeccion)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FUR3')
        resultset['error'] = True

    return resultset


def fetch_user_by_entryname_raw(entry_name, entry_value):
    resultset = get_default_resultset()

    try:
        resultset['resultset'] = db.users.find_one({entry_name: entry_value})
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FUBEN1')
        resultset['error'] = True

    return resultset


def get_user_id_as_string(user):
    # log_debug( 'get_user_id_as_string) user[]: {}'.format(user) )
    return str(user['_id'])


def create_user(json):
    resultset = get_default_resultset()

    if not 'email' in json:
        resultset['error_message'] = 'error: Email wasn\'t specified [CU1].'
    elif json['email'] == 'foo@baz.com' and not ('pytest_run' in json and json['pytest_run'] == 1):
            resultset['error_message'] = 'error: User {} is invalid [CU2].'.format(json['email'])
    elif not check_email(json['email']):
        resultset['error_message'] = 'error: Malformed email {} [CU3].'.format(json['email'])
    else:
        db_row = fetch_user_by_entryname_raw('email', json['email'])
        if db_row['resultset']:
            resultset['error_message'] = 'User {} already exists [CU4].'.format(json['email'])
        elif db_row['error']:
            resultset['error_message'] = db_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    if 'passcode' in json:
        json['passcode'] = encrypt_password(json['passcode'])
    json['creation_date'] = json['update_date'] = current_datetime_timestamp()

    try:
        resultset['resultset']['_id'] = str(db.users.insert_one(json).inserted_id)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'CU5')
        resultset['error'] = True
    else:
        resultset['resultset']['rows_affected'] = '1'

    return resultset


def update_users(record):
    resultset = get_default_resultset()

    mandatory_elements = {
        'firstname',
        'lastname',
        'creation_date',
        'birthday',
        'email',
        'height',
        'height_unit',
        'weight',
        'weight_unit',
        'training_days',
        'training_hour',
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
        resultset['error_message'] = 'Missing mandatory elements: {} [UU1].'.format(resultset['error_message'])
        resultset['error'] = True
        return resultset

    updated_record['update_date'] = current_datetime_timestamp()
    if 'passcode' in record and record['passcode']:
        updated_record['passcode'] = encrypt_password(record['passcode'])

    if '_id' not in record and 'id' in record:
        record['_id'] = record['id']
        del record['id']

    if '_id' in updated_record:
        del updated_record['_id']

    try:
        resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(record['_id'])}, {
            '$set': updated_record
        }).modified_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'UU2')
        resultset['error'] = True

    return resultset


def delete_user(user_id):
    resultset = get_default_resultset()

    db_row = fetch_user_by_entryname_raw('_id', ObjectId(user_id))
    if not db_row['resultset']:
        resultset['error_message'] = 'error: User {} doesn\'t exist [DU1].'.format(user_id)
    elif db_row['error']:
        resultset['error_message'] = db_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    try:
        resultset['resultset']['rows_affected'] = str(db.users.delete_one({'_id': ObjectId(user_id)}).deleted_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'DU2')
        resultset['error'] = True

    return resultset


# ----- food_times


def fetch_user_food_times(users_id, filters=None, skip=0, limit=None):
    array_field = 'food_times'
    resultset = get_default_resultset()
    proyeccion = {
        array_field: 1
    }
    db_parent_row = fetch_user_raw(users_id, proyeccion)
    if not db_parent_row['resultset']:
        resultset['error_message'] = 'Id {} doesn\'t exist [FUFT1].'.format(users_id)
    elif db_parent_row['error']:
        resultset['error_message'] = db_parent_row['error_message']

    if resultset['error_message']:
        resultset['error'] = True
        return resultset

    response = db_parent_row['resultset'].get(array_field, [])

    if filters != None:
        for key in filters:
            response = list(filter(lambda x: x[key] == filters[key], response))

    if skip == None:
        skip = 0
    response = list(islice(islice(response, skip, None), limit))

    try:
        resultset['resultset'] = dumps(response)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'FUFT2')
        resultset['error'] = True

    return resultset


def add_food_times_to_user(json):
    array_field = 'food_times'
    parent_key_field = 'user_id'
    resultset = get_default_resultset()
    try:
        resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json[parent_key_field])}, {
            '$addToSet': {array_field: json[array_field]}}).modified_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'AFTTU1')
        resultset['error'] = True
    return resultset


def remove_food_times_to_user(json):
    log_debug('')
    log_debug('remove_food_times_to_user - json')
    log_debug(json)
    log_debug('')
    array_field = 'food_times'
    array_key_field = 'food_moment_id'
    parent_key_field = 'user_id'
    array_field_in_json = array_field
    if '{}_old'.format(array_field_in_json) in json:
        # This is for deletion of older entry when the key field has been changed
        array_field_in_json = '{}_old'.format(array_field_in_json)
    log_debug('')
    log_debug('$pull from "{}", array_key_field={}, array_field_in_json={}, key value to REMOVE={}'.format(array_field, array_key_field, array_field_in_json, json[array_field_in_json][array_key_field]))
    log_debug('')
    resultset = get_default_resultset()
    try:
        resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json[parent_key_field])}, {
            '$pull': {array_field: {array_key_field: json[array_field_in_json][array_key_field]}}
        }).modified_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'RFTTU')
        resultset['error'] = True
    return resultset


# ----- user_history


def add_user_history_to_user(json):
    array_field = 'user_history'
    resultset = get_default_resultset()
    try:
        # curso = consultar_curso_por_id_proyeccion(json['id_curso'], proyeccion={'nombre': 1})
        resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json['user_id'])}, {
            '$addToSet': {'user_history': json['user_history']}}).modified_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'AUHTU1')
        resultset['error'] = True
    return resultset


def remove_user_history_to_user(json):
    array_field = 'user_history'
    resultset = get_default_resultset()
    try:
        resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json['user_id'])}, {
            '$pull': {'user_history': {'date': json['date']}}
        }).modified_count)
    except BaseException as err:
        resultset['error_message'] = get_standard_base_exception_msg(err, 'RUHTU')
        resultset['error'] = True
    return resultset


# ----------------------- security_groups -----------------------

# Table: security_groups
# PK: _id
# Fields:
#     _id
#     name

# ----------------------- menu_options -----------------------

# Table: menu_options
# PK: _id
# Fields:
#     _id
#     name

# ----------------------- security_group_access -----------------------

# Table: security_group_access
# PK: _id
# Index: user_id
# Index: date
# Fields:
#     _id
#     group_id -> security_groups._id
#     menu_option_id -> menu_options._id
#     access_type

# ----------------------- security_group_users -----------------------

# Table: security_group_users
# PK: _id
# Index: user_id
# Index: group_id
# Fields:
#     _id
#     group_id -> security_groups._id
#     user_id -> users._id

# ----------------------- -----------------------
# ----------------------- -----------------------
# ----------------------- -----------------------

# ----------------------- food_moments -----------------------

# Table: food_moments
# PK: _id
# Fields:
#     _id
#     name

# ----------------------- food_ingredients -----------------------

# Table: food_ingredients
# PK: _id
# Fields:
#     _id
#     name
#     portion
#     unit
#     calories
#     portion_factor

# ----------------------- user_food_daily -----------------------

# Table: user_food_daily
# PK: _id
# Fields:
#     _id
#     user_id -> users._id
#     date
#     foods: 
#       [
#           {
#               food_moment_id -> food_moments._id
#               food_ingredient_id -> food_ingredients._id
#               qty
#               calories
#           }
#       ]

# ----------------------- -----------------------
