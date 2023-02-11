import chalicelib

import pytest


@pytest.fixture
def client():
    app = chalicelib.create_app()
    with app.test_client() as client:
        yield client
