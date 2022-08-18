import pytest

import os
import jwt
import datetime
import base64

from test_010_api import client


test_email = 'foo@baz.com'
test_password = 'Q12!K34$j56_79'
dummy_user_id = '6174cf3e31d0f78fb73abf55'

test_food_moment_id = '6174cf3e31d0f78fb73abf54'
test_users_record = {
    'firstname': 'Carlos',
    'lastname': 'Ramirez',
    'passcode': test_password,
    'creation_date': 1635033994,
    'birthday': -131760000,
    'email': test_email,
    'height': '1.70',
    'height_unit': 'm',
    'weight': '74',
    'weight_unit': 'kg',
    'training_days': 'MTWXFS',
    'training_hour': '17:00',
    'pytest_run': 1
}
header_token_entry_name = 'x-access-tokens'


def pytest_namespace():
    return {
        'session_token': None,
        'new_user_id': None,
        'new_food_moment_id': None
    }


def test_create_user(client):
    """Test Users creation."""

    def token_encode(user):
        token = jwt.encode(
            {
                'public_id': str(user['_id']),
                'exp' : 
                    datetime.datetime.utcnow() + 
                    datetime.timedelta(minutes=30)
            },
            os.environ['FYNAPP_SECRET_KEY'],
            algorithm="HS256"
        )
        return token
    user = {'_id': dummy_user_id}
    token = token_encode(user)
    headers =  {header_token_entry_name: token}
    rv = client.post('/users', json=dict(test_users_record), headers=dict(headers))
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'resultset' in json_data
    assert '_id' in json_data['resultset']
    pytest.new_user_id = json_data['resultset']['_id'] 
    assert not pytest.new_user_id is None
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_login(client):
    """Test user login."""

    auth = {
        'username': test_users_record['email'],
        'password': test_users_record['passcode'],
    }
    valid_credentials = base64.b64encode(str.encode("{}:{}".format(auth['username'], auth['password']))).decode("utf-8")
    rv = client.post('/users/login', headers={"Authorization": "Basic " + valid_credentials})
    assert not b'could not verify' in rv.data
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'token' in json_data['resultset']
    pytest.session_token = json_data['resultset']['token'] 
