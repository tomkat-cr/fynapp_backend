from bson.json_util import dumps, ObjectId
from flask import current_app
from pymongo import MongoClient, DESCENDING
from werkzeug.local import LocalProxy

import hashlib


# Este método se encarga de configurar la conexión con la base de datos
def get_db():
    fynapp_db_uri = current_app.config['FYNAPP_DB_URI']
    fynapp_db_name = current_app.config['FYNAPP_DB_NAME']
    client = MongoClient(fynapp_db_uri)
    # Devuelve el nombre de base de datos que se pasa por env var.
    return client.get_database(fynapp_db_name)


# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)


def test_connection():
    return dumps(db.list_collection_names())


def collection_stats(collection_nombre):
    return dumps(db.command('collstats', collection_nombre))

# ...
# ...
# ...

# ----------------------- users -----------------------

# Table: users
# PK: _id
# Fields:
#     _id
#     passcode
#     firsname
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
    return dumps(db.users.find_one({'_id': ObjectId(users_id)}))


def create_user(json):
    if ('passcode' in json):
        json['passcode'] = encrypt_password(json['passcode'])
    # if (not 'food_times' in json):
    #     json['food_times'] = []
    # if (not 'user_history' in json):
    #     json['user_history'] = []
    return str(db.users.insert_one(json).inserted_id)


def update_users(record):
    updated_record = {
        'firsname': record['firsname'],
        'lastname': record['lastname'],
        'creation_date': record['creation_date'],
        'birthday': record['birthday'],
        'email': record['email'],
        'height': record['height'],
        'height_unit': record['height_unit'],
        'training_days': record['training_days'],
        'training_hour': record['training_hour'],
    }
    if ('passcode' in record):
        updated_record['passcode'] = encrypt_password(record['passcode'])
    return str(db.users.update_one({'_id': ObjectId(record['_id'])}, {
        '$set': updated_record
    }).modified_count)


def encrypt_password(passcode):
    return hashlib.md5(passcode.encode('utf8')).hexdigest()


def delete_user(user_id):
    return str(db.users.delete_one({'_id': ObjectId(user_id)}).deleted_count)


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
