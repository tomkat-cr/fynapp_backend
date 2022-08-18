from bson.json_util import dumps
from flask import current_app
from pymongo import MongoClient
from werkzeug.local import LocalProxy

from fynapp_api.util.app_logger import log_debug, log_warning

# ----------------------- Db General -----------------------

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
