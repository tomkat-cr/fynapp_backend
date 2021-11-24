from bson.json_util import dumps, ObjectId
from flask import current_app
from pymongo import MongoClient, DESCENDING
from werkzeug.local import LocalProxy

# import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

from flask import request, jsonify
import uuid
import jwt
import datetime
from functools import wraps

from fynapp_api.util.app_logger import log_debug, log_warning
from fynapp_api.util.utilities import check_email, standard_error_return

# Este método se encarga de configurar la conexión con la base de datos
def get_db():
    fynapp_db_uri = current_app.config['FYNAPP_DB_URI']
    fynapp_db_name = current_app.config['FYNAPP_DB_NAME']
    client = MongoClient(fynapp_db_uri)
    # Devuelve el nombre de base de datos que se pasa por env var.
    return client.get_database(fynapp_db_name)


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

header_token_entry_name = 'x-access-tokens'


def test_connection():
    return dumps(db.list_collection_names())


def collection_stats(collection_nombre):
    return dumps(db.command('collstats', collection_nombre))


# ----------------------- jwt -----------------------


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # log_warning( 'token_required | request.headers: {}'.format(request.headers) )
        if header_token_entry_name in request.headers:
            token = request.headers[header_token_entry_name]
        if not token:
            return standard_error_return('a valid token is missing')
            # return jsonify({'message': 'a valid token is missing', 'error': True})
        # log_warning( 'la clave: {}'.format(current_app.config['FYNAPP_SECRET_KEY']) )
        # log_warning( 'el token: {}'.format(token) )
        try:
            data = jwt.decode(token, current_app.config['FYNAPP_SECRET_KEY'], algorithms="HS256")
            # current_user = fetch_user_raw(users_id=data['public_id'])
        except:
            return standard_error_return('token is invalid')
            # return jsonify({'message': 'token is invalid', 'error': True})
        # return f(current_user, *args, **kwargs)
        return f(*args, **kwargs)
    return decorator


def token_encode(user):
    token = jwt.encode(
        {
            'public_id': get_user_id_as_string(user),
            'exp' : 
                datetime.datetime.utcnow() + 
                datetime.timedelta(minutes=30)
        },
        current_app.config['FYNAPP_SECRET_KEY'],
        algorithm="HS256"
    )
    return token

# ...
# ...
# ...

# ----------------------- users -----------------------

# Table: users
# PK: _id
# Fields:
#     _id
#     passcode
#     firstname
#     lastname
#     creation_date
#     birthday
#     email
#     height
#     height_unit
#     training_days
#     training_hour
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


def fetch_users_list(skip, limit):
    proyeccion = {'passcode': 0}
    return dumps(db.users.find({}, proyeccion).skip(int(skip)).limit(int(limit)))


def fetch_user(users_id):
    existing_user = fetch_user_raw(users_id)
    if not existing_user:
        return {'error': 'UserId {} doesn\'t exist [FU1].'.format(users_id)}
    return dumps(existing_user)


def fetch_user_raw(users_id):
    return db.users.find_one({'_id': ObjectId(users_id)})


def fetch_user_by_entryname_raw(entry_name, entry_value):
    return db.users.find_one({entry_name: entry_value})


def get_user_id_as_string(user):
    return str(user['_id'])


def create_user(json):
    if not 'email' in json:
        return 'error: Email wasn\'t specified [CU1].'
    if json['email'] == 'foo@baz.com' and not ('pytest_run' in json and json['pytest_run'] == 1):
        return 'error: User {} is invalid [CU2].'.format(json['email'])
    if not check_email(json['email']):
        return 'error: Malformed email {} [CU3].'.format(json['email'])
    existing_user = fetch_user_by_entryname_raw('email', json['email'])
    if existing_user:
        return 'error: User {} already exists [CU4].'.format(json['email'])
    if ('passcode' in json):
        json['passcode'] = encrypt_password(json['passcode'])
    return str(db.users.insert_one(json).inserted_id)


def update_users(record):
    updated_record = {
        'firstname': record['firstname'],
        'lastname': record['lastname'],
        'creation_date': record['creation_date'],
        'birthday': record['birthday'],
        'email': record['email'],
        'height': record['height'],
        'height_unit': record['height_unit'],
        'training_days': record['training_days'],
        'training_hour': record['training_hour'],
    }
    if ('passcode' in record and record['passcode']):
        updated_record['passcode'] = encrypt_password(record['passcode'])
    return str(db.users.update_one({'_id': ObjectId(record['_id'])}, {
        '$set': updated_record
    }).modified_count)


def delete_user(user_id):
    existing_user = fetch_user_by_entryname_raw('_id', ObjectId(user_id))
    if not existing_user:
        return 'error: User {} doesn\'t exist [DU1].'.format(user_id)
    return str(db.users.delete_one({'_id': ObjectId(user_id)}).deleted_count)


# ----- passwords


def encrypt_password(passcode):
    return generate_password_hash(passcode, method='sha256')
    # return hashlib.md5(passcode.encode('utf8')).hexdigest()


def verify_password(user_password, auth_password):
    return check_password_hash(user_password, auth_password)


# ----- food_times


def add_food_times_to_user(json):
    return str(db.users.update_one({'_id': ObjectId(json['user_id'])}, {
        '$addToSet': {'food_times': json['food_times']}}).modified_count)


def remove_food_times_to_user(json):
    return str(db.users.update_one({'_id': ObjectId(json['user_id'])}, {
        '$pull': {'food_times': {'food_moment_id': json['food_moment_id']}}
    }).modified_count)


# ----- user_history


def add_user_history_to_user(json):
    # curso = consultar_curso_por_id_proyeccion(json['id_curso'], proyeccion={'nombre': 1})
    return str(db.users.update_one({'_id': ObjectId(json['user_id'])}, {
        '$addToSet': {'user_history': json['user_history']}}).modified_count)


def remove_user_history_to_user(json):
    return str(db.users.update_one({'_id': ObjectId(json['user_id'])}, {
        '$pull': {'user_history': {'date': json['date']}}
    }).modified_count)


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
