import pytest
from app import app

# Example data for testing
test_property = {
    "name": "Test Property",
    "address": "123 Test Ave",
    "external_url": "https://test.com/property",
}


@pytest.fixture
def client():
    app.config.from_object("test_config")
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "OK"}


def test_create_property(client):
    response = client.post("/properties", json=test_property)
    assert response.status_code == 200
    assert "Property created" in response.json["message"]


def test_get_properties(client):
    response = client.get("/properties")
    assert response.status_code == 200
    assert isinstance(response.json, list)
