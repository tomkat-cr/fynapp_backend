from __future__ import annotations
# from types import NoneType
from bson.json_util import dumps
from flask import current_app
from werkzeug.local import LocalProxy

from pymongo import MongoClient

import boto3

from .app_logger import log_debug, log_warning


# ----------------------- Factory Methods -----------------------


class ObjectFactory:
    def __init__(self):
        self._builders = {}

    def register_builder(self, key, builder):
        self._builders[key] = builder

    def create(self, key, **kwargs):
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


# ----------------------- Db Abstract -----------------------


class DbAbstract:
    def __init__(self, app_config, **_ignored):
        self._app_config = app_config
        self._db = self.get_db_conection()
        self.create_tables()


    def get_db(self):
        return self._db


    def get_db_conection(self):
        return {}


    def test_connection(self):
        return dumps({})


    def list_collections(self, collection_name = None):
        return {}


    def collection_stats(self, collection_name = None):
        return dumps(self.list_collections(collection_name))


    def create_tables():
        return True


    def table_exists(table_name: str) -> bool:
        return True


# ----------------------- MongoDb  -----------------------


class MongodbService(DbAbstract):
    def get_db_conection(self):
        client = MongoClient(self._app_config['DB_CONFIG']['mongodb_uri'])
        return client.get_database(self._app_config['DB_CONFIG']['mongodb_db_name'])


    def test_connection(self):
        return dumps(self._db.list_collection_names())


    def collection_stats(self, collection_name):
        return dumps(self._db.command('collstats', collection_name))


class MongodbServiceBuilder(DbAbstract):
    def __init__(self):
        self._instance = None


    def __call__(self, app_config, **_ignored):
        if not self._instance:
            self._instance = MongodbService(app_config)
        return self._instance


# ----------------------- DynamoDb  -----------------------


class DynamoDbTableAbstract:
    def __init__(self, item_structure, db_conection):
        log_debug('>>--> DynamoDbTableAbstract | __init__ | item_structure: '+str(item_structure))
        self.set_table_name(item_structure['table_name'])
        self.set_key_schema(item_structure['key_schema'])
        self.set_attribute_definitions(item_structure['attribute_definitions'])
        self._db_conection = db_conection


    def set_table_name(self, table_name):
        self._table_name = table_name


    def set_key_schema(self, key_schema):
        self._key_schema = key_schema


    def set_attribute_definitions(self, attribute_definitions):
        self._attribute_definitions = attribute_definitions


    def get_table_name(self):
        return self._table_name


    def get_key_schema(self):
        return self._key_schema


    def get_attribute_definitions(self):
        return self._attribute_definitions

    # resultset['resultset'] = db.users.find_one({'_id': id}, proyeccion)

    def find_one(self, query_params, proyection = {}):
        log_debug('>>--> find_one() | table: '+self.get_table_name()+' | query_params: ' + str(query_params))
        table = self._db_conection.Table(self.get_table_name())
        keys = {}
        for key_schema_item in self.get_key_schema():
            key_name = key_schema_item['AttributeName']
            keys[key_name] = query_params.get(key_name if key_name != '_id' else 'id')

        response = table.get_item(
            Key=keys
        )
        log_debug(response)
        item = response.get('Item')
        return item

    # resultset['resultset'] = db.users.find({}, proyeccion).skip(int(skip)).limit(int(limit))

    # resultset['resultset']['_id'] = str(db.users.insert_one(json).inserted_id)
    
    # resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(record['_id'])}, {'$set': updated_record}).modified_count)
    
    # resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json[parent_key_field])}, {'$pull': {array_field: {array_key_field: json[array_field_in_json][array_key_field]}}}).modified_count)
    
    # resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json[parent_key_field])}, {'$addToSet': {array_field: json[array_field]}}).modified_count)

    # resultset['resultset']['rows_affected'] = str(db.users.delete_one({'_id': ObjectId(user_id)}).deleted_count)


class DynamodbServiceSuper(DbAbstract):
    def get_db_conection(self):
        self._db = boto3.resource('dynamodb')
        self.create_table_name_propeties()
        return self._db


    def create_table_name_propeties(self):
        item_list = self.list_collections()
        for item_name in item_list:
            log_debug('>>--> Setting property: '+item_name)
            self.__setattr__(item_name, DynamoDbTableAbstract(item_list[item_name], self._db))


    def list_collection_names(self):
        return map(lambda item_name: item_name, self.list_collections())


    def get_db(self):
        return self


    def test_connection(self):
        return dumps(self.list_collection_names())


    def create_tables(self):
        default_provisioned_throughput = {
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
        item_list = self.list_collections()
        for item_name in item_list:
            log_debug('>>--> Creating Dynamodb Table: '+item_name)
            if self.table_exists(item_name):
                continue
            # Create table in Dynamodb
            table = self._db.create_table(
                TableName=item_name,
                KeySchema=item_list[item_name]['key_schema'],
                AttributeDefinitions=item_list[item_name]['attribute_definitions'],
                ProvisionedThroughput=item_list[item_name].get('provisioned_throughput', default_provisioned_throughput)
            )
            # Wait until the table exists.
            table.wait_until_exists()
            # Print out some data about the table.
            log_debug('>>--> Dynamodb Table: '+item_name + ' CREATED! - table.item_count: '+str(table.item_count))

        return True


    def table_exists(self, table_name: str) -> bool:
        try:
            self._db.Table(table_name).table_status
        except self._db.meta.client.exceptions.ResourceNotFoundException:
            return False
        return True


class DynamodbService(DynamodbServiceSuper):
    def list_collections(self):
        return {
            "users" : {
                'table_name': 'users',
                'key_schema': [
                    {
                        'AttributeName': 'email',
                        'KeyType': 'HASH'
                    },
                    # {
                    #     'AttributeName': 'id',
                    #     'KeyType': 'RANGE'
                    # }
                ],
                'attribute_definitions': [
                    {
                        'AttributeName': 'email',
                        'AttributeType': 'S'
                    },
                    # {
                    #     'AttributeName': 'id',
                    #     'AttributeType': 'S'
                    # },
                ],
            },
            "food_moments" : {
                'table_name': 'food_moments',
                'key_schema': [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    },
                ],
                'attribute_definitions': [
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    },
                ],
            },
            "designers_flutter_test" : {
                'table_name': 'designers_flutter_test',
                'key_schema': [
                    {
                        'AttributeName': 'id',
                        'KeyType': 'HASH'
                    },
                ],
                'attribute_definitions': [
                    {
                        'AttributeName': 'id',
                        'AttributeType': 'S'
                    },
                ],

            },
        }


class DynamodbServiceBuilder(DbAbstract):
    def __init__(self):
        self._instance = None

    def __call__(self, app_config, **_ignored):
        if not self._instance:
            self._instance = DynamodbService(app_config)
        return self._instance


# ----------------------- Db General -----------------------


def get_db_factory():
    factory = ObjectFactory()
    current_db_engine = current_app.config['DB_ENGINE']
    # if current_app.config['DB_ENGINE'] == 'DYNAMO_DB':
    #     factory.register_builder('DYNAMO_DB', DynamodbServiceBuilder())
    # else:
    #     current_db_engine = 'MONGO_DB'
    #     factory.register_builder('MONGO_DB', MongodbServiceBuilder())
    factory.register_builder('DYNAMO_DB', DynamodbServiceBuilder())
    factory.register_builder('MONGO_DB', MongodbServiceBuilder())
    return factory.create(current_db_engine, app_config = current_app.config)


db_factory = LocalProxy(get_db_factory)


def get_db_engine():
    return db_factory.get_db()


db = LocalProxy(get_db_engine)


def test_connection():
    return db_factory.test_connection()