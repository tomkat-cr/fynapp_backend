from array import array
from test_fynapp_api import client
import pytest


test_food_moment_id = '6174cf3e31d0f78fb73abf54'
test_users_record = {
    'firsname': 'Carlos',
    'lastname': 'Ramirez',
    'passcode': '12345678',
    'creation_date': 1635033994,
    'birthday': -131760000,
    'email': 'foo@baz.com',
    'height': '76.0',
    'tall': '1.70',
    'height_unit': 'kg',
    'tall_unit': 'meters',
    'training_days': 'MTWXFS',
    'training_hour': '17:00',
}


def pytest_namespace():
    return {'new_user_id': None}


def test_connection(client):
    """Test connection by querying the collections list (tables)."""

    rv = client.get('/users/test')
    json_data = rv.get_json()
    assert 'collections' in json_data
    assert 'users' in json_data['collections']
    # assert b'collections' in rv.data
    # assert b'users' in rv.data


def test_create_user(client):
    """Test Users creation."""

    rv = client.post('/users', json=dict(test_users_record))
    json_data = rv.get_json()
    assert '_id' in json_data
    pytest.new_user_id = json_data['_id'] 
    assert not pytest.new_user_id is None
    print('new_user_id = {}'.format(pytest.new_user_id))


def test_fetch_users_list(client):
    """Test Users list."""

    rv = client.get('/users?skip={}&limit={}'.format(0, 1))
    json_data = rv.get_json()
    assert 'users' in json_data
    assert isinstance(json_data['users'], list)
    assert len(json_data['users']) == 1
    assert 'firsname' in json_data['users'][0]
    assert 'lastname' in json_data['users'][0]
    assert 'passcode' not in json_data['users'][0]


def test_fetch_user(client):
    """Test fetch one user by its id."""

    rv = client.get('/users?id={}'.format(pytest.new_user_id))
    json_data = rv.get_json()
    assert 'user' in json_data
    assert '_id' in json_data['user']
    assert {'$oid': pytest.new_user_id} == json_data['user']['_id']
    assert 'firsname' in json_data['user']
    assert test_users_record['firsname'] == json_data['user']['firsname']
    assert 'lastname' in json_data['user']
    assert test_users_record['lastname'] == json_data['user']['lastname']
    assert 'passcode' in json_data['user']


def test_update_users(client):
    """Test update some user data."""

    updated_record = dict(test_users_record)
    updated_record['_id'] = pytest.new_user_id
    updated_record['firsname'] = 'Jose'
    updated_record['lastname'] = 'Divo'
    updated_record['passcode'] = '87654321'

    rv = client.put('/users', json=dict(updated_record))
    json_data = rv.get_json()
    assert 'updates' in json_data
    assert json_data['updates'] == '1'


# ----- food_times


def test_add_food_times_to_user(client):
    """Test add a food_times item to the test user."""

    rv = client.put('/users/add-food-times-to-user', json={
            'user_id': pytest.new_user_id,
            'food_times': {
                'food_moment_id': test_food_moment_id,
                'food_time': '12:00'
            }
        }
    )
    json_data = rv.get_json()
    assert 'updates' in json_data
    assert json_data['updates'] == '1'

def test_remove_food_times_to_user(client):
    """Test delete a food_times item from the test user."""

    rv = client.delete('/users/add-food-times-to-user', json={
            'user_id': pytest.new_user_id,
            'food_moment_id': test_food_moment_id
        }
    )
    json_data = rv.get_json()
    assert 'deletions' in json_data
    assert json_data['deletions'] == '1'


# ----- user_history


def test_add_user_history_to_user(client):
    """Test add a user_history item to the test user."""

    rv = client.put('/users/add-user-history-to-user', json={
            'user_id': pytest.new_user_id,
            'user_history': {
                'date': test_users_record['creation_date'],
                'goals': 'Loose weight',
                'weight': '70',
                'weight_unit': 'kg'
            }
        }
    )
    json_data = rv.get_json()
    assert 'updates' in json_data
    assert json_data['updates'] == '1'


def test_remove_user_history_to_user(client):
    """Test delete a user_history item from the test user."""

    rv = client.delete('/users/add-user-history-to-user', json={
            'user_id': pytest.new_user_id,
            'date': test_users_record['creation_date'],
        }
    )
    json_data = rv.get_json()
    assert 'deletions' in json_data
    assert json_data['deletions'] == '1'


# ----- Sprint cleaning


def test_delete_user(client):
    """Test delete the test user."""

    rv = client.delete('/users?id={}'.format(pytest.new_user_id))
    json_data = rv.get_json()
    assert 'deletions' in json_data
    assert json_data['deletions'] == '1'
