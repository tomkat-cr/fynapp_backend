import fynapp_api

import pytest


@pytest.fixture
def client():
    app = fynapp_api.create_app()
    with app.test_client() as client:
        yield client
