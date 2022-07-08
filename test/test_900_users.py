import pytest
import json
import os
import base64

from test_010_api import client
from test_020_common import header_token_entry_name
from test_020_common import test_email, test_password, test_food_moment_id, test_users_record



def test_create_superadmin_user(client):
    """Test super-admin User creation."""

    auth = {
        'username': os.environ.get('FYNAPP_SUPERADMIN_EMAIL', 'super@fynapp.com'),
        'password': test_password,
    }
    valid_credentials = base64.b64encode(str.encode("{}:{}".format(auth['username'], auth['password']))).decode("utf-8")
    rv = client.post('/users/supad-create', headers={"Authorization": "Basic " + valid_credentials})
    assert rv.status_code == 400
    assert b'could not verify [SAC3]' in rv.data or b'User already exists [SAC4]' in rv.data


def test_connection(client):
    """Test connection by querying the collections list (tables)."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users/test', headers=dict(headers))
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'resultset' in json_data
    assert 'collections' in json_data['resultset']
    assert 'users' in json_data['resultset']['collections']


def test_create_user_again(client):
    """Test fail trying to create the test user again."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.post('/users', json=dict(test_users_record), headers=dict(headers))
    assert rv.status_code == 400
    assert bytes('User '+test_email+' already exists [CU4]', 'utf-8') in rv.data


def test_fetch_users_list(client):
    """Test Users list."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users?skip={}&limit={}'.format(0, 1), headers=dict(headers))
    assert rv.status_code == 200
    json_data_raw = rv.get_json()
    # {'error': False, 'error_message': None, 'resultset': '[{"_id": {"$oid": "6234804f0990244c025c599c"}, "birthday": -1317...1.70", "tall_unit": "meters", "training_days": "MTWXFS", "training_hour": "17:00", "update_date": 1647607887.898997}]'}
    assert 'resultset' in json_data_raw
    json_data = json.loads(json_data_raw['resultset'])
    assert isinstance(json_data, list)
    assert len(json_data) == 1
    assert 'firstname' in json_data[0]
    assert 'lastname' in json_data[0]
    assert 'passcode' not in json_data[0]
    assert 'creation_date' in json_data[0]
    assert 'update_date' in json_data[0]
    row_to_compare = dict(test_users_record)
    del row_to_compare['passcode']
    row_to_compare['_id'] = json_data[0]['_id']
    row_to_compare['creation_date'] = json_data[0]['creation_date']
    row_to_compare['update_date'] = json_data[0]['update_date']
    assert json_data[0] == row_to_compare


def test_fetch_user(client):
    """Test fetch one user by its id."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users?id={}'.format(pytest.new_user_id), headers=dict(headers))
    assert rv.status_code == 200
    json_data_raw = rv.get_json()
    assert 'resultset' in json_data_raw
    json_data = json.loads(json_data_raw['resultset'])
    assert '_id' in json_data
    assert {'$oid': pytest.new_user_id} == json_data['_id']
    assert 'firstname' in json_data
    assert test_users_record['firstname'] == json_data['firstname']
    assert 'lastname' in json_data
    assert test_users_record['lastname'] == json_data['lastname']
    assert 'passcode' in json_data


def test_update_users(client):
    """Test update some user data."""

    updated_record = dict(test_users_record)
    updated_record['_id'] = pytest.new_user_id
    updated_record['firstname'] = 'Jose'
    updated_record['lastname'] = 'Divo'
    updated_record['passcode'] = '87654321'

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/users', json=dict(updated_record), headers=dict(headers))
    assert rv.status_code == 200
    json_data = rv.get_json()
    # {'error': False, 'error_message': '', 'resultset': {'rows_affected': '1'}}
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_failed_update_users(client):
    """Test failed update some user data."""

    updated_record = dict(test_users_record)
    del updated_record['weight']
    del updated_record['weight_unit']
    updated_record['_id'] = pytest.new_user_id
    updated_record['firstname'] = 'Jose'
    updated_record['lastname'] = 'Divo'
    updated_record['passcode'] = '87654321'

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/users', json=dict(updated_record), headers=dict(headers))
    assert rv.status_code == 400
    #
    # {'error': True, 'error_message': 'Missing mandatory elements:  weight,  weight_unit [UU1].', 'resultset': {}}
    # json_data = rv.get_json()
    # assert 'resultset' in json_data
    # assert 'error' in json_data
    # assert json_data['resultset']['error'] == True
    # assert 'error_message' in json_data
    # assert json_data['resultset']['error_message'] == 'Missing mandatory elements:  weight,  weight_unit [UU1]'
    # assert 'resultset' in json_data
    # assert json_data['resultset'] == {}
    #
    # Missing mandatory elements: weight_unit, weight [UU1]
    # Missing mandatory elements: weight, weight_unit [UU1]
    assert (
        b'Missing mandatory elements: weight_unit, weight [UU1]' in rv.data
        or
        b'Missing mandatory elements: weight, weight_unit [UU1]' in rv.data
    )


# ----- food_times


def test_add_food_times_to_user(client):
    """Test add a food_times item to the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/users/user-food-times', json={
            'user_id': pytest.new_user_id,
            'food_times': {
                'food_moment_id': test_food_moment_id,
                'food_time': '12:00'
            }
        }, headers=dict(headers)
    )
    assert rv.status_code == 200
    json_data = rv.get_json()
    # {'error': False, 'error_message': None, 'resultset': {'rows_affected': '1'}}
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_fetch_food_times_from_user(client):
    """Test food_times list."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users/user-food-times?skip={}&limit={}&user_id={}'.format(
        0, 1, pytest.new_user_id), headers=dict(headers))
    assert rv.status_code == 200
    json_data_raw = rv.get_json()
    assert 'resultset' in json_data_raw
    json_data = json.loads(json_data_raw['resultset'])
    assert isinstance(json_data, list)
    assert len(json_data) == 1
    assert 'food_moment_id' in json_data[0]
    assert 'food_time' in json_data[0]
    assert json_data[0] == {
        'food_moment_id': test_food_moment_id,
        'food_time': '12:00'
    }


def test_update_food_times_to_user(client):
    """Test update a food_times item in the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.post('/users/user-food-times', json={
            'user_id': pytest.new_user_id,
            'food_times': {
                'food_moment_id': test_food_moment_id,
                'food_time': '22:00'
            }
        }, headers=dict(headers)
    )
    assert rv.status_code == 200
    json_data = rv.get_json()
    # {'error': False, 'error_message': None, 'resultset': {'rows_affected': '1'}}
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_remove_food_times_to_user(client):
    """Test delete a food_times item from the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/users/user-food-times', json={
            'user_id': pytest.new_user_id,
            'food_times': {
                'food_moment_id': test_food_moment_id
            }
        }, headers=dict(headers)
    )
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


# ----- user_history


def test_add_user_history_to_user(client):
    """Test add a user_history item to the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/users/user-user-history', json={
            'user_id': pytest.new_user_id,
            'user_history': {
                'date': test_users_record['creation_date'],
                'goals': 'Loose weight',
                'weight': '70',
                'weight_unit': 'kg'
            }
        }, headers=dict(headers)
    )
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_fetch_user_history_from_user(client):
    """Test user_history list."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/users/user-user-history?skip={}&limit={}&user_id={}'.format(
        0, 1, pytest.new_user_id), headers=dict(headers))
    assert rv.status_code == 200
    json_data_raw = rv.get_json()
    assert 'resultset' in json_data_raw
    json_data = json.loads(json_data_raw['resultset'])
    assert isinstance(json_data, list)
    assert len(json_data) == 1
    assert 'date' in json_data[0]
    assert 'goals' in json_data[0]
    assert 'weight' in json_data[0]
    assert 'weight_unit' in json_data[0]
    assert json_data[0] == {
        'date': test_users_record['creation_date'],
        'goals': 'Loose weight',
        'weight': '70',
        'weight_unit': 'kg'
    }


def test_update_user_history_to_user(client):
    """Test update a user_history item to the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.post('/users/user-user-history', json={
            'user_id': pytest.new_user_id,
            'user_history': {
                'date': test_users_record['creation_date'],
                'goals': 'Get fit',
                'weight': '82',
                'weight_unit': 'kg'
            }
        }, headers=dict(headers)
    )
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_remove_user_history_to_user(client):
    """Test delete a user_history item from the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/users/user-user-history', json={
            'user_id': pytest.new_user_id,
            'user_history': {
                'date': test_users_record['creation_date'],
            }
        }, headers=dict(headers)
    )
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


# ----- Sprint cleaning


def test_delete_user(client):
    """Test delete the test user."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/users?id={}'.format(pytest.new_user_id), headers=dict(headers))
    assert rv.status_code == 200
    json_data = rv.get_json()
    # {'error': False, 'error_message': None, 'resultset': {'rows_affected': '1'}}
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_delete_user_again(client):
    """Test fail trying to delete the test user again."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/users?id={}'.format(pytest.new_user_id), headers=dict(headers))
    assert rv.status_code == 400
    # error: User 62348adbfbe27f42c4837015 doesn't exist [DU1].
    assert b'error: User ' in rv.data and b'doesn\'t exist [DU1]' in rv.data
