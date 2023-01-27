from __future__ import annotations
from bson.json_util import dumps, ObjectId
from flask import current_app
from werkzeug.local import LocalProxy
# import uuid
import json
from decimal import Decimal

from pymongo import MongoClient

import boto3
# from boto3.dynamodb.conditions import Key

from .app_logger import log_debug, log_warning
from fynapp_api.models.dynamodb_table_structures \
    import dynamodb_table_structures, \
    DEFAULT_WRITE_CAPACITY_UNITS, DEFAULT_READ_CAPACITY_UNITS


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

    def list_collections(self, collection_name=None):
        return {}

    def collection_stats(self, collection_name=None):
        return dumps(self.list_collections(collection_name))

    def create_tables(self):
        return True

    def table_exists(self, table_name: str) -> bool:
        return True

# ----------------------- MongoDb  -----------------------


class MongodbService(DbAbstract):
    def get_db_conection(self):
        client = MongoClient(self._app_config['DB_CONFIG']['mongodb_uri'])
        return client.get_database(
            self._app_config['DB_CONFIG']['mongodb_db_name']
        )

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


class DynamoDbUtilities:
    def new_id(self):
        """Generate mongodb styled _id
        """
        # google: python generate unique _id like mongodb
        # https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/
        # id = uuid.uuid1()
        # uuid1() includes the used of MAC address of computer,
        # and hence can compromise the privacy,
        # even though it provides UNIQUENES.
        # return id.hex
        # RESULT: bson.errors.InvalidId: '48a8b1a021b611edbf5a0e4c731ac1c1'
        # is not a valid ObjectId, it must be a 12-byte input or a
        # 24-character hex string | vs 6302ded424b11a2032d7c562
        # SOLUTION: https://api.mongodb.com/python/1.11/api/bson/objectid.html
        return str(ObjectId())

    def id_addition(self, row):
        """Convert _id to be mongodb styled,
           for example to send it to the react frontend
           expecting it as a $oid
        """
        if 'id' in row:
            row['_id'] = ObjectId(row['id'])
        elif '_id' in row and isinstance(row['_id'], str):
            # row['id'] = row['_id']
            row['_id'] = ObjectId(row['_id'])
        return row

    def id_conversion(self, key_set):
        """To avoid error working internally with mongodb styled _id
        """
        log_debug('\\\\\\\ id_conversion | key_set BEFORE: ' + str(key_set))
        if '_id' in key_set and not isinstance(key_set['_id'], str):
            key_set['_id'] = str(key_set['_id'])
        log_debug('\\\\\\\ id_conversion | key_set AFTER: ' + str(key_set))
        return key_set

    def prepare_item_with_no_floats(self, item):
        """To be used before sending dict to DynamoDb for inserts/updates
        """
        return json.loads(json.dumps(item), parse_float=Decimal)

    def remove_decimal_types(self, item):
        """To be used before sending responses to entity
        """
        log_debug('====> remove_decimal_types | item BEFORE: '+str(item))
        item = self.id_conversion(item)
        # item = json.loads(json.dumps(item, default=str))
        item = json.loads(json.dumps(item, default=float))
        item = self.id_addition(item)
        log_debug('====> remove_decimal_types | item AFTER: '+str(item))
        return item


class DynamoDbFindIterator(DynamoDbUtilities):
    def __init__(self, data_set):
        log_debug(
            '>>--> DynamoDbFindIterator | __init__() | data_set: ' +
            str(data_set)
        )
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
        log_debug(
            '>>--> DynamoDbFindIterator | __iter__() | self.num: ' +
            str(self._num)
        )
        return self

    def __next__(self):
        log_debug(
            '>>--> DynamoDbFindIterator | __next__() | self.num: ' +
            str(self._num) + ' | len(self._data_set): ' +
            str(len(self._data_set))
        )
        if (not self._limit or self._num <= self._limit) and \
           self._data_set and self._num < len(self._data_set):
            # _result = self.prepare_item_with_no_floats(
            #   self.id_addition(self._data_set[self._num])
            # )
            _result = self.remove_decimal_types(
                self.id_addition(self._data_set[self._num])
            )
            log_debug(
                '>>--> DynamoDbFindIterator | __next__() | _result: ' +
                str(_result)
            )
            # _result = self.id_addition(self._data_set[self._num])
            self._num += 1
            return _result
        else:
            raise StopIteration


class DynamoDbTableAbstract(DynamoDbUtilities):
    def __init__(self, item_structure, db_conection):
        log_debug(
            '>>--> DynamoDbTableAbstract | __init__ | item_structure: ' +
            str(item_structure)
        )
        self.set_table_name(item_structure['TableName'])
        self.set_key_schema(item_structure['KeySchema'])
        self.set_global_secondary_indexes(
            item_structure.get('GlobalSecondaryIndexes', [])
        )
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
        log_debug('|||---> element_name: '+str(element_name))
        # return element_name['AttributeName'] \
        #   if element_name['AttributeName'] != '_id' else 'id'
        return element_name['AttributeName']

    def get_condition_expresion_values(self, data_list, separator=' AND '):
        # condition_values = list(map(lambda item: list(
        #   map(lambda key: {':'+key: item[key]}, item.keys())
        # ), data_list))
        condition_values = {}
        for item in data_list:
            for key in item.keys():
                condition_values = condition_values | {':'+key: item[key]}
        expresion_parts = list(map(lambda item: list(
            map(lambda key: key + ' = :' + key, item.keys())
        ), data_list))
        condition_expresion = separator.join(expresion_parts[0])
        # return condition_values[0][0], condition_expresion
        return condition_values, condition_expresion

    # Look for keys in partition/sort key
    def get_primary_keys(self, query_params):
        keys = list(
            filter(
                lambda key: query_params.get(
                    self.element_name(key)
                    # OJO
                    # ) != None, self.get_key_schema()
                ) is not None, self.get_key_schema()
            )
        )
        keys = list(
            map(
                lambda key: {self.element_name(key): query_params.get(
                    self.element_name(key)
                )}, keys
            )
        )
        return keys[0] if len(keys) > 0 else None

    # Look for keys in global secondary indexes
    def get_global_secondary_indexes_keys(self, query_params):
        # reduced_indexes = list(map(lambda global_index: {
        #     global_index["IndexName"]: list(
        #       map(lambda key: self.element_name(
        #           key
        #       ), global_index["KeySchema"])
        #     )
        # }, self.get_global_secondary_indexes()))

        reduced_indexes = [{
            'name': global_index["IndexName"], 
            'keys': list(map(
                lambda key: self.element_name(key), global_index["KeySchema"]
            ))
        } for global_index in self.get_global_secondary_indexes()]

        query_keys = list(query_params.keys())

        index_item = list(filter(
            lambda index: set(query_keys).issubset(
                index['keys']
            ), reduced_indexes
        ))

        keys = None
        index_name = None
        if index_item:
            index_name = index_item[0]['name']
            keys = list(map(
                lambda key: {key: query_params[key]}, index_item[0]['keys']
            ))

        log_debug('|-|--> get_global_secondary_indexes_keys | keys: ' +
                  str(keys) + ' | reduced_indexes: ' + str(reduced_indexes) +
                  ' | index_name: ' + str(index_name) + ' | query_keys: ' +
                  str(query_keys))
        return keys, index_name

    def generic_query(self, query_params, proyection={}):
        log_debug('>>--> generic_query() | table: ' + self.get_table_name() +
                  ' | query_params: ' + str(query_params) + ' | proyection: ' +
                  str(proyection))

        table = self._db_conection.Table(self.get_table_name())

        if not query_params or len(query_params) == 0:
            response = table.scan()
            return response.get('Items') if response else None

        query_params = self.id_conversion(query_params)
        keys = self.get_primary_keys(query_params)

        if keys:
            log_debug('===> Keys found: '+str(keys))
            response = table.get_item(
                Key=keys
            )
            log_debug(response)
            return self.remove_decimal_types(
                response.get('Item')
            ) if response else None

        keys, index_name = self.get_global_secondary_indexes_keys(query_params)

        if not keys:
            condition_values, condition_expresion = \
                self.get_condition_expresion_values([query_params])
            log_debug(
                'No keys found... perform fullscan | condition_values: ' +
                str(condition_values) + ' | condition_expresion: ' +
                str(condition_expresion)
            )
            response = table.scan(
                ExpressionAttributeValues=condition_values,
                FilterExpression=condition_expresion
            )
            return self.remove_decimal_types(
                response.get('Items')[0]
            ) if response else None

        log_debug('===> secondary Keys found: ' + str(keys))
        log_debug(keys)
        condition_values, condition_expresion = \
            self.get_condition_expresion_values(keys)
        log_debug(
            '===> secondary Keys pre query elements | condition_values: ' +
            str(condition_values) + ' | condition_expresion:' +
            str(condition_expresion)
        )
        response = table.query(
            IndexName=index_name,
            ExpressionAttributeValues=condition_values,
            KeyConditionExpression=condition_expresion
        )

        log_debug(response)
        if response and len(response.get('Items', [])) > 0:
            return self.remove_decimal_types(response.get('Items')[0])
        return None

    # resultset['resultset'] = db.users.find({}, proyeccion).skip(
    #   int(skip)
    # ).limit(int(limit))
    def find(self, query_params, proyection={}):
        log_debug(
            '>>--> find() | table: ' + self.get_table_name() +
            ' | query_params: ' + str(query_params) +
            ' | proyection: ' + str(proyection)
        )
        return DynamoDbFindIterator(
            self.generic_query(query_params, proyection)
        )

    # resultset['resultset'] = db.users.find_one({'_id': id}, proyeccion)
    def find_one(self, query_params, proyection={}):
        log_debug(
            '>>--> find_one() | table: ' + self.get_table_name() +
            ' | query_params: ' + str(query_params) +
            ' | proyection: ' + str(proyection)
        )
        return self.generic_query(query_params, proyection)

    # resultset['resultset']['_id'] = str(
    #   db.users.insert_one(json).inserted_id
    # )
    def insert_one(self, new_item):
        table = self._db_conection.Table(self.get_table_name())
        self.inserted_id = None
        new_item['_id'] = self.new_id()
        new_item = self.prepare_item_with_no_floats(new_item)
        try:
            result = table.put_item(
                Item=new_item
            )
            self.inserted_id = new_item['_id']
            log_debug(
                '>>--> RESULT insert_one() | table: ' + self.get_table_name() +
                ' | new_item: ' + str(new_item) + ' | self.inserted_id: ' +
                str(self.inserted_id) + ' | result: ' + str(result)
            )
            return self
        except Exception as e:
            log_warning(
                'insert_one: Error creating Item [IO_ERR_010]: ' + str(e)
            )
        return False

    # Case 1: $set
    # resultset['resultset']['rows_affected'] = str(
    #   db.users.update_one(
    #      {'_id': ObjectId(record['_id'])},
    #      {'$set': updated_record}
    #   ).modified_count
    # )
    #
    # Case 2: $addToSet
    # resultset['resultset']['rows_affected'] = str(
    #   db.users.update_one(
    #       {'_id': ObjectId(json[parent_key_field])},
    #       {'$addToSet': {array_field: json[array_field]}}
    #   ).modified_count
    # )
    #
    # Case 3: $pull
    # resultset['resultset']['rows_affected'] = str(
    #   db.users.update_one(
    #       {'_id': ObjectId(json[parent_key_field])},
    #       {'$pull': {
    #           array_field: {
    #               array_key_field: json[array_field_in_json][array_key_field]
    #           }
    #       }}
    #   ).modified_count
    # )
    def update_one(self, key_set, update_set_original):
        log_debug(
            '>>--> update_one() | table: ' + self.get_table_name() +
            ' | key_set: ' + str(key_set)
        )
        table = self._db_conection.Table(self.get_table_name())
        key_set = self.prepare_item_with_no_floats(self.id_conversion(key_set))
        self.modified_count = None
        keys = self.get_primary_keys(key_set)
        if not keys:
            log_warning('update_one: No partition keys found [UO_ERR_010]')
            return False
        if '$set' in update_set_original:
            update_set = update_set_original['$set']
            pass
        elif '$addToSet' in update_set_original:
            pass
        elif '$pull' in update_set_original:
            pass
        update_set = self.prepare_item_with_no_floats(update_set)
        expression_attribute_values, update_expression = \
            self.get_condition_expresion_values([update_set], ', ')
        try:
            log_debug(
                '>>--> BEFORE update_one() | table: ' + self.get_table_name() +
                ' | update_set: ' + str(update_set) + ' | keys: ' +
                str(keys) + ' | self.modified_count: ' +
                str(self.modified_count) + ' | expression_attribute_values: ' +
                str(expression_attribute_values) + ' | update_expression: ' +
                str(update_expression)
            )
            result = table.update_item(
                Key=keys,
                UpdateExpression="SET " + update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="UPDATED_NEW"
            )
            self.modified_count = 1
            log_debug(
                '>>--> RESULT update_one() | table: ' + self.get_table_name() +
                ' | update_set: ' + str(update_set) + ' | keys: ' +
                str(keys) + ' | self.modified_count: ' +
                str(self.modified_count) + ' | expression_attribute_values: ' +
                str(expression_attribute_values) + ' | update_expression: ' +
                str(update_expression) + ' | result: ' + str(result)
            )
            return self
        except Exception as e:
            log_warning(
                'update_one: Error ipdating Item [UO_ERR_020]: ' + str(e)
            )
        return False

    # resultset['resultset']['rows_affected'] = str(db.users.delete_one(
    #   {'_id': ObjectId(user_id)}).deleted_count
    # )
    def delete_one(self, key_set):
        log_debug(
            '>>--> delete_one() | table: ' + self.get_table_name() +
            ' | key_set: ' + str(key_set)
        )
        table = self._db_conection.Table(self.get_table_name())
        key_set = self.id_conversion(key_set)
        self.deleted_count = None
        keys = self.get_primary_keys(key_set)
        if not keys:
            log_warning('delete_one: No partition keys found [DO_ERR_010]')
            return False
        try:
            result = table.delete_item(
                Key=keys
            )
            self.deleted_count = 1
            log_debug(
                '>>--> RESULT delete_one() | table: ' + self.get_table_name() +
                ' | key_set: ' + str(key_set) + ' | keys: ' + str(keys) +
                ' | self.deleted_count: ' + str(self.deleted_count) +
                ' | result: ' + str(result)
            )
            return self
        except Exception as e:
            log_warning(
                'delete_one: Error ipdating Item [DO_ERR_020]: ' + str(e)
            )
        return False


class DynamodbServiceSuper(DbAbstract, DynamoDbUtilities):
    def get_db_conection(self):
        self._db = boto3.resource('dynamodb')
        self.create_table_name_propeties()
        return self._db

    def create_table_name_propeties(self):
        item_list = self.list_collections()
        for item_name in item_list:
            log_debug('>>--> Setting property: '+item_name)
            self.__setattr__(item_name, DynamoDbTableAbstract(
                item_list[item_name], self._db
            ))

    def list_collection_names(self):
        return map(lambda item_name: item_name, self.list_collections())

    def get_db(self):
        return self

    def test_connection(self):
        return dumps(self.list_collection_names())

    def create_tables(self):
        default_provisioned_throughput = {
            'ReadCapacityUnits': DEFAULT_READ_CAPACITY_UNITS,
            'WriteCapacityUnits': DEFAULT_WRITE_CAPACITY_UNITS
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
                AttributeDefinitions=item_list[item_name][
                    'AttributeDefinitions'
                ],
                ProvisionedThroughput=item_list[item_name].get(
                    'provisioned_throughput', default_provisioned_throughput
                ),
                GlobalSecondaryIndexes=item_list[item_name].get(
                    'GlobalSecondaryIndexes', []
                ),
            )
            # Wait until the table exists.
            table.wait_until_exists()
            # Print out some data about the table.
            log_debug(
                '>>--> Dynamodb Table: '+item_name +
                ' CREATED! - table.item_count: ' + str(table.item_count)
            )

        return True

    def table_exists(self, table_name: str) -> bool:
        try:
            self._db.Table(table_name).table_status
        except self._db.meta.client.exceptions.ResourceNotFoundException:
            return False
        return True


class DynamodbService(DynamodbServiceSuper):
    def list_collections(self):
        return dynamodb_table_structures()


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
    return factory.create(current_db_engine, app_config=current_app.config)


db_factory = LocalProxy(get_db_factory)


def get_db_engine():
    return db_factory.get_db()


db = LocalProxy(get_db_engine)


def test_connection():
    return db_factory.test_connection()
