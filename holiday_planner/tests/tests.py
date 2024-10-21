import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    client = APIClient()
    return client


def test_core(api_client):
    response = api_client.get("/api/hello/")

    assert response.status_code == 200
    assert response.data == {"message": "Hello, Django!"}
