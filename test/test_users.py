from array import array
from test_fynapp_api import client
import pytest

# from flask import current_app
import os
import jwt
import datetime
import base64


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
    'height': '76.0',
    'tall': '1.70',
    'height_unit': 'kg',
    'tall_unit': 'meters',
    'training_days': 'MTWXFS',
    'training_hour': '17:00',
    'pytest_run': 1
}
header_token_entry_name = 'x-access-tokens'

def pytest_namespace():
    return {
        'new_user_id': None,
        'session_token': None,
    }


def test_create_superadmin_user(client):
    """Test super-admin User creation."""

    auth = {
        'username': os.environ.get('FYNAPP_SUPERADMIN_EMAIL', 'super@fynapp.com'),
        'password': test_password,
    }
    valid_credentials = base64.b64encode(str.encode("{}:{}".format(auth['username'], auth['password']))).decode("utf-8")
    rv = client.post('/users/supad-create', headers={"Authorization": "Basic " + valid_credentials})
    assert b'could not verify [SAC3]' in rv.data or b'User already exists [SAC4]' in rv.data


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
    json_data = rv.get_json()
    assert '_id' in json_data
    pytest.new_user_id = json_data['_id'] 
    assert not pytest.new_user_id is None
    print('new_user_id = {}'.format(pytest.new_user_id))


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
    assert 'token' in json_data
    pytest.session_token = json_data['token'] 


def test_connection(client):
    """Test connection by querying the collections list (tables)."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users/test', headers=dict(headers))
    json_data = rv.get_json()
    assert 'collections' in json_data
    assert 'users' in json_data['collections']
    # assert b'collections' in rv.data
    # assert b'users' in rv.data


def test_fetch_users_list(client):
    """Test Users list."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users?skip={}&limit={}'.format(0, 1), headers=dict(headers))
    json_data = rv.get_json()
    assert 'users' in json_data
    assert isinstance(json_data['users'], list)
    assert len(json_data['users']) == 1
    assert 'firstname' in json_data['users'][0]
    assert 'lastname' in json_data['users'][0]
    assert 'passcode' not in json_data['users'][0]


def test_fetch_user(client):
    """Test fetch one user by its id."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users?id={}'.format(pytest.new_user_id), headers=dict(headers))
    json_data = rv.get_json()
    assert 'user' in json_data
    assert '_id' in json_data['user']
    assert {'$oid': pytest.new_user_id} == json_data['user']['_id']
    assert 'firstname' in json_data['user']
    assert test_users_record['firstname'] == json_data['user']['firstname']
    assert 'lastname' in json_data['user']
    assert test_users_record['lastname'] == json_data['user']['lastname']
    assert 'passcode' in json_data['user']


def test_update_users(client):
    """Test update some user data."""

    updated_record = dict(test_users_record)
    updated_record['_id'] = pytest.new_user_id
    updated_record['firstname'] = 'Jose'
    updated_record['lastname'] = 'Divo'
    updated_record['passcode'] = '87654321'

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/users', json=dict(updated_record), headers=dict(headers))
    json_data = rv.get_json()
    assert 'updates' in json_data
    assert json_data['updates'] == '1'


# ----- food_times


def test_user_food_times(client):
    """Test add a food_times item to the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/users/add-food-times-to-user', json={
            'user_id': pytest.new_user_id,
            'food_times': {
                'food_moment_id': test_food_moment_id,
                'food_time': '12:00'
            }
        }, headers=dict(headers)
    )
    json_data = rv.get_json()
    assert 'updates' in json_data
    assert json_data['updates'] == '1'

def test_remove_food_times_to_user(client):
    """Test delete a food_times item from the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/users/add-food-times-to-user', json={
            'user_id': pytest.new_user_id,
            'food_moment_id': test_food_moment_id
        }, headers=dict(headers)
    )
    json_data = rv.get_json()
    assert 'deletions' in json_data
    assert json_data['deletions'] == '1'


# ----- user_history


def test_add_user_history_to_user(client):
    """Test add a user_history item to the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/users/add-user-history-to-user', json={
            'user_id': pytest.new_user_id,
            'user_history': {
                'date': test_users_record['creation_date'],
                'goals': 'Loose weight',
                'weight': '70',
                'weight_unit': 'kg'
            }
        }, headers=dict(headers)
    )
    json_data = rv.get_json()
    assert 'updates' in json_data
    assert json_data['updates'] == '1'


def test_remove_user_history_to_user(client):
    """Test delete a user_history item from the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/users/add-user-history-to-user', json={
            'user_id': pytest.new_user_id,
            'date': test_users_record['creation_date'],
        }, headers=dict(headers)
    )
    json_data = rv.get_json()
    assert 'deletions' in json_data
    assert json_data['deletions'] == '1'


# ----- Sprint cleaning


def test_delete_user(client):
    """Test delete the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/users?id={}'.format(pytest.new_user_id), headers=dict(headers))
    json_data = rv.get_json()
    assert 'deletions' in json_data
    assert json_data['deletions'] == '1'
