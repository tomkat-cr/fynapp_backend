from __future__ import annotations
from bson.json_util import dumps, ObjectId
from flask import current_app
from werkzeug.local import LocalProxy
import uuid
  
from pymongo import MongoClient

import boto3
from boto3.dynamodb.conditions import Key

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


    def create_tables(self):
        return True


    def table_exists(self, table_name: str) -> bool:
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


class DynamoDbIdUtilities:
    def new_id(self):
        # google: python generate unique _id like mongodb
        # https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/
        id = uuid.uuid1()
        # uuid1() includes the used of MAC address of computer, 
        # and hence can compromise the privacy, even though it provides UNIQUENES.
        return id.hex


    def id_addition(self, row):
        if 'id' in row:
            row['_id'] = ObjectId(row['id'])
        elif '_id' in row and isinstance(row['_id'], str):
            row['id'] = row['_id']
            row['_id'] = ObjectId(row['_id'])
        return row


    def id_conversion(self, key_set):
        if '_id' in key_set and not isinstance(key_set['_id'], str):
            key_set['_id'] = str(key_set['_id'])
        return key_set


class DynamoDbFindIterator(DynamoDbIdUtilities):
    def __init__(self, data_set):
        log_debug('>>--> DynamoDbFindIterator | __init__() | data_set: '+str(data_set))
        self._data_set = data_set
        self._skip = 0
        self._limit = None


    def skip(self, skip):
        log_debug('>>--> DynamoDbFindIterator | skip() | skip: '+str(skip))
        self._skip = skip
        return self


    def limit(self, limit):
        log_debug('>>--> DynamoDbFindIterator | limit() | limit: '+str(limit))
        self._limit = limit
        return self


    def __iter__(self):
        self._num = self._skip
        log_debug('>>--> DynamoDbFindIterator | __iter__() | self.num: '+str(self._num))
        return self


    def __next__(self):
        log_debug('>>--> DynamoDbFindIterator | __next__() | self.num: '+str(self._num)+' | len(self._data_set): '+str(len(self._data_set)))
        if (not self._limit or self._num <= self._limit) and self._data_set and self._num < len(self._data_set):
            _result = self.id_addition(self._data_set[self._num])
            self._num += 1
            return _result
        else:
            raise StopIteration


class DynamoDbTableAbstract:
    def __init__(self, item_structure, db_conection):
        log_debug('>>--> DynamoDbTableAbstract | __init__ | item_structure: '+str(item_structure))
        self.set_table_name(item_structure['TableName'])
        self.set_key_schema(item_structure['KeySchema'])
        self.set_global_secondary_indexes(item_structure.get('GlobalSecondaryIndexes', []))
        self.set_attribute_definitions(item_structure['AttributeDefinitions'])
        self._db_conection = db_conection


    def set_table_name(self, table_name):
        self._table_name = table_name


    def set_key_schema(self, key_schema):
        self._key_schema = key_schema


    def set_attribute_definitions(self, attribute_definitions):
        self._attribute_definitions = attribute_definitions


    def set_global_secondary_indexes(self, global_secondary_indexes):
        self._global_secondary_indexes = global_secondary_indexes


    def get_table_name(self):
        return self._table_name


    def get_key_schema(self):
        return self._key_schema


    def get_attribute_definitions(self):
        return self._attribute_definitions


    def get_global_secondary_indexes(self):
        return self._global_secondary_indexes


    def element_name(self, element_name):
        log_debug("||--> element_name")
        log_debug(element_name)
        return element_name['AttributeName'] if element_name['AttributeName'] != '_id' else 'id'


    def get_condition_expresion_values(self, keys):
        condition_values = list(map(lambda key: {':'+key['name']: key['value']}, keys))
        condition_expresion = ' AND '.join(
            list(map(lambda key: '#'+key['name'] + ' = :' + key['name'], keys))
        )
        return condition_values, condition_expresion


    # Look for keys in partition/sort key
    def get_primary_keys(self, query_params):
        keys = list(filter(lambda key: query_params.get(self.element_name(key)) != None, self.get_key_schema()))
        keys = list(map(lambda key: {self.element_name(key): query_params.get(self.element_name(key))}, keys))
        return keys


    # Look for keys in global secondary indexes
    def get_global_secondary_indexes_keys(self, query_params):
        keys = list(
            filter(
                lambda key: query_params.get(self.element_name(key)) != None, 
                list(
                    map(
                        lambda key: key, 
                        self.get_global_secondary_indexes().get("KeySchema", [])
                    )
                )
            )
        )
        keys = list(map(lambda key: {"name": self.element_name(key), "value": query_params.get(self.element_name(key))}, keys))
        return keys


    def generic_query(self, query_params, proyection = {}):
        log_debug('>>--> generic_query() | table: ' + self.get_table_name() + ' | query_params: ' + str(query_params)+ ' | proyection: ' + str(proyection))

        table = self._db_conection.Table(self.get_table_name())

        if not query_params or len(query_params) == 0:
            response = table.scan()
            return response.get('Items') if response else None

        keys = self.get_primary_keys(query_params)

        if keys:
            response = table.get_item(
                Key=keys
            )
            log_debug(response)
            return response.get('Item') if response else None

        keys = self.get_global_secondary_indexes_keys(query_params)

        if not keys:
            log_debug('No keys found...')
            keys = list(map(lambda key: {"name": key, "value": query_params.get(key)}, list(query_params.keys())))
            condition_values, condition_expresion = self.get_condition_expresion_values(keys)
            response = table.scan(
                ExpressionAttributeValues = condition_values,
                FilterExpression = condition_expresion
            )
            return response.get('Items')[0] if response else None

        log_debug('===> Keys found...')
        log_debug(keys)
        if len(keys) == 1:
            response = table.query(
                KeyConditionExpression = Key(keys[0]['name']).eq(keys[0]['value'])
            )
        else:
            condition_values, condition_expresion = self.get_condition_expresion_values(keys)
            response = table.query(
                ExpressionAttributeValues = condition_values,
                KeyConditionExpression = condition_expresion
            )

        log_debug(response)
        return response.get('Items')[0] if response else None


    # resultset['resultset'] = db.users.find({}, proyeccion).skip(int(skip)).limit(int(limit))
    def find(self, query_params, proyection = {}):
        log_debug('>>--> find() | table: ' + self.get_table_name() + ' | query_params: ' + str(query_params)+ ' | proyection: ' + str(proyection))
        return DynamoDbFindIterator(self.generic_query(query_params, proyection))


    # resultset['resultset'] = db.users.find_one({'_id': id}, proyeccion)
    def find_one(self, query_params, proyection = {}):
        log_debug('>>--> find_one() | table: ' + self.get_table_name() + ' | query_params: ' + str(query_params)+ ' | proyection: ' + str(proyection))
        return self.generic_query(query_params, proyection)


    # resultset['resultset']['_id'] = str(db.users.insert_one(json).inserted_id)
    def insert_one(self, new_item):
        log_debug('>>--> insert_one() | table: ' + self.get_table_name() + ' | new_item: ' + str(new_item))
        table = self._db_conection.Table(self.get_table_name())
        response = {
            'inserted_id': self.new_id()
        }
        new_item['_id'] = response['inserted_id']
        result = table.put_item(
            Item=new_item
        )
        log_debug(response)
        return response if result else False


    # Case 1: $set
    # resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(record['_id'])}, {'$set': updated_record}).modified_count)
    # Case 2: $addToSet
    # resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json[parent_key_field])}, {'$addToSet': {array_field: json[array_field]}}).modified_count)
    # Case 3: $pull
    # resultset['resultset']['rows_affected'] = str(db.users.update_one({'_id': ObjectId(json[parent_key_field])}, {'$pull': {array_field: {array_key_field: json[array_field_in_json][array_key_field]}}}).modified_count)
    def update_one(self, key_set, update_set):
        log_debug('>>--> update_one() | table: ' + self.get_table_name() + ' | key_set: ' + str(key_set))
        table = self._db_conection.Table(self.get_table_name())
        key_set = self.id_conversion(key_set)
        response = {
            'modified_count': 1
        }
        keys = self.get_primary_keys(key_set)
        if not keys:
            return False
        expression_attribute_values, update_expression = self.get_condition_expresion_values(keys)
        result = table.update_item(
            Key=keys,
            UpdateExpression="SET title=:r",
            ExpressionAttributeValues={
                ':r': data['title']
            },
            ReturnValues="UPDATED_NEW"
        )
        log_debug(response)
        return response if result else False




    # resultset['resultset']['rows_affected'] = str(db.users.delete_one({'_id': ObjectId(user_id)}).deleted_count)
    def delete_one(self, key_set):
        log_debug('>>--> delete_one() | table: ' + self.get_table_name() + ' | key_set: ' + str(key_set))
        table = self._db_conection.Table(self.get_table_name())
        key_set = self.id_conversion(key_set)
        response = {
            'deleted_count': 1
        }
        keys = self.get_primary_keys(key_set)
        if not keys:
            return False
        result = table.delete_item(
            Key=keys
        )
        log_debug(response)
        return response if result else False


class DynamodbServiceSuper(DbAbstract, DynamoDbIdUtilities):
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
                KeySchema=item_list[item_name]['KeySchema'],
                AttributeDefinitions=item_list[item_name]['AttributeDefinitions'],
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
                'TableName': 'users',
                'KeySchema': [
                    {
                        'AttributeName': '_id',
                        'KeyType': 'RANGE'
                    }
                ],
                'GlobalSecondaryIndexes': {
                    'KeySchema': [
                        {
                            'AttributeName': 'email',
                            'KeyType': 'HASH'
                        },
                    ],
                },
                'AttributeDefinitions': [
                    {
                        'AttributeName': 'email',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': '_id',
                        'AttributeType': 'S'
                    },
                ],
            },
            "food_moments" : {
                'TableName': 'food_moments',
                'KeySchema': [
                    {
                        'AttributeName': '_id',
                        'KeyType': 'HASH'
                    },
                ],
                'AttributeDefinitions': [
                    {
                        'AttributeName': '_id',
                        'AttributeType': 'S'
                    },
                ],
            },
            "designers_flutter_test" : {
                'TableName': 'designers_flutter_test',
                'KeySchema': [
                    {
                        'AttributeName': '_id',
                        'KeyType': 'HASH'
                    },
                ],
                'AttributeDefinitions': [
                    {
                        'AttributeName': '_id',
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
    factory.register_builder('DYNAMO_DB', DynamodbServiceBuilder())
    factory.register_builder('MONGO_DB', MongodbServiceBuilder())
    return factory.create(current_db_engine, app_config = current_app.config)


db_factory = LocalProxy(get_db_factory)


def get_db_engine():
    return db_factory.get_db()


db = LocalProxy(get_db_engine)


def test_connection():
    return db_factory.test_connection()