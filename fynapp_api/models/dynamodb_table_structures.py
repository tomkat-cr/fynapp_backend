# dynamodb_table_structures.py


DEFAULT_WRITE_CAPACITY_UNITS = 1
DEFAULT_READ_CAPACITY_UNITS = 1


def dynamodb_table_structures():
    return {
        "users": {
            'TableName': 'users',
            'KeySchema': [
                {
                    'AttributeName': '_id',
                    'KeyType': 'HASH'
                }
            ],
            'GlobalSecondaryIndexes': [
                {
                    'KeySchema': [
                        {
                            'AttributeName': 'email',
                            'KeyType': 'HASH'
                        },
                    ],
                    "IndexName": "Email-index",
                    "Projection": {
                        "ProjectionType": "ALL"
                    },
                    "ProvisionedThroughput": {
                        # "NumberOfDecreasesToday": 0,
                        "ReadCapacityUnits": DEFAULT_READ_CAPACITY_UNITS,
                        "WriteCapacityUnits": DEFAULT_WRITE_CAPACITY_UNITS,
                    },
                },
                # {
                #     'KeySchema': [
                #         {
                #             'AttributeName': '_id',
                #             'KeyType': 'HASH'
                #         },
                #         {
                #             'AttributeName': 'email',
                #             'KeyType': 'RANGE'
                #         },
                #     ],
                #     "IndexName": "Email-index-2",
                #     "Projection": {
                #         "ProjectionType": "ALL"
                #     },
                #     "ProvisionedThroughput": {
                #         # "NumberOfDecreasesToday": 0,
                #         "ReadCapacityUnits": DEFAULT_READ_CAPACITY_UNITS,
                #         "WriteCapacityUnits": DEFAULT_WRITE_CAPACITY_UNITS,
                #     },
                # },
            ],
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
        "food_moments": {
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
        "designers_flutter_test": {
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
