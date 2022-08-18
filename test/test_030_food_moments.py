import pytest

from test_010_api import client
from test_020_common import header_token_entry_name

import json


test_food_moments_record = {
    'name': "Breakfast",
}


def test_create_food_moment(client):
    """Test food_moment creation."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.post('/food_moments', json=dict(test_food_moments_record), headers=dict(headers))
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert 'resultset' in json_data
    assert '_id' in json_data['resultset']
    pytest.new_food_moment_id = json_data['resultset']['_id'] 
    assert not pytest.new_food_moment_id is None
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_create_food_moment_again(client):
    """Test fail trying to create the test food_moment again."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.post('/food_moments', json=dict(test_food_moments_record), headers=dict(headers))
    assert rv.status_code == 400
    assert bytes('Food Moment '+test_food_moments_record['name']+' already exists [CFM4]', 'utf-8') in rv.data


def test_fetch_food_moments_list(client):
    """Test food_moments list."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/food_moments?skip={}&limit={}'.format(0, 1), headers=dict(headers))
    assert rv.status_code == 200
    json_data_raw = rv.get_json()
    # {'error': False, 'error_message': None, 'resultset': '[{"_id": {"$oid": "6234804f0990244c025c599c"}, "name": "Breakfast", "creation_date": 1647607887.898997, "update_date": 1647607887.898997}]'}
    assert 'resultset' in json_data_raw
    json_data = json.loads(json_data_raw['resultset'])
    assert isinstance(json_data, list)
    assert len(json_data) == 1
    assert 'name' in json_data[0]
    assert 'creation_date' in json_data[0]
    assert 'update_date' in json_data[0]


def test_fetch_food_moment(client):
    """Test fetch one food_moment by its id."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.get('/food_moments?id={}'.format(pytest.new_food_moment_id), headers=dict(headers))
    assert rv.status_code == 200
    json_data_raw = rv.get_json()
    assert 'resultset' in json_data_raw
    json_data = json.loads(json_data_raw['resultset'])
    assert '_id' in json_data
    assert {'$oid': pytest.new_food_moment_id} == json_data['_id']
    assert 'name' in json_data
    assert test_food_moments_record['name'] == json_data['name']


def test_update_food_moments(client):
    """Test update some food_moment data."""

    updated_record = dict(test_food_moments_record)
    updated_record['_id'] = pytest.new_food_moment_id
    updated_record['name'] = 'Lunch'

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/food_moments', json=dict(updated_record), headers=dict(headers))
    assert rv.status_code == 200
    json_data = rv.get_json()
    # {'error': False, 'error_message': '', 'resultset': {'rows_affected': '1'}}
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_failed_update_food_moments(client):
    """Test failed update some food_moment data."""

    updated_record = dict(test_food_moments_record)
    del updated_record['name']
    updated_record['_id'] = pytest.new_food_moment_id

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.put('/food_moments', json=dict(updated_record), headers=dict(headers))
    assert rv.status_code == 400
    # Missing mandatory elements: name [UFM1]
    assert (
        b'Missing mandatory elements: name [UFM1]' in rv.data
    )


# ----- Sprint cleaning


def test_delete_food_moment(client):
    """Test delete the test food_moment."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/food_moments?id={}'.format(pytest.new_food_moment_id), headers=dict(headers))
    assert rv.status_code == 200
    json_data = rv.get_json()
    # {'error': False, 'error_message': None, 'resultset': {'rows_affected': '1'}}
    assert 'resultset' in json_data
    assert 'rows_affected' in json_data['resultset']
    assert json_data['resultset']['rows_affected'] == '1'


def test_delete_food_moment_again(client):
    """Test fail trying to delete the test food_moment again."""

    headers = {header_token_entry_name: pytest.session_token}
    rv = client.delete('/food_moments?id={}'.format(pytest.new_food_moment_id), headers=dict(headers))
    assert rv.status_code == 400
    # error: Food Moment 62348adbfbe27f42c4837015 doesn't exist [DU1].
    assert b'error: Food Moment ' in rv.data and b'doesn\'t exist [DFM1]' in rv.data
