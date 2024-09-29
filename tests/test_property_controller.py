import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from uuid import UUID
from controllers.property_controller import property_bp
from models.property import Property

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(property_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_jwt_required():
    with patch('controllers.property_controller.jwt_required') as mock:
        yield mock

@pytest.fixture
def mock_property_service():
    with patch('controllers.property_controller.PropertyService') as mock:
        yield mock

def test_create_property(client, mock_jwt_required, mock_property_service):
    mock_property_service.create_property.return_value = Property(id=UUID('12345678-1234-5678-1234-567812345678'), name="Test Property")
    
    response = client.post('/create', json={
        "name": "Test Property",
        "address": "123 Test St",
        "price": 100000
    })
    
    assert response.status_code == 201
    assert response.json['name'] == "Test Property"
    assert 'id' in response.json

def test_get_property(client, mock_jwt_required, mock_property_service):
    property_id = UUID('12345678-1234-5678-1234-567812345678')
    mock_property_service.get_property.return_value = Property(id=property_id, name="Test Property")
    
    response = client.get(f'/view/{property_id}')
    
    assert response.status_code == 200
    assert response.json['name'] == "Test Property"
    assert response.json['id'] == str(property_id)

def test_update_property(client, mock_jwt_required, mock_property_service):
    property_id = UUID('12345678-1234-5678-1234-567812345678')
    mock_property_service.update_property.return_value = Property(id=property_id, name="Updated Property")
    
    response = client.put(f'/update/{property_id}', json={
        "name": "Updated Property"
    }, headers={'x-user-id': 'test-user-id'})
    
    assert response.status_code == 200
    assert response.json['name'] == "Updated Property"

def test_delete_property(client, mock_jwt_required, mock_property_service):
    property_id = UUID('12345678-1234-5678-1234-567812345678')
    mock_property_service.delete_property.return_value = True
    
    response = client.delete(f'/delete/{property_id}', headers={'x-user-id': 'test-user-id'})
    
    assert response.status_code == 200
    assert response.json['message'] == "Property deleted successfully"

def test_list_properties(client, mock_jwt_required, mock_property_service):
    mock_properties = [
        Property(id=UUID('12345678-1234-5678-1234-567812345678'), name="Property 1"),
        Property(id=UUID('87654321-8765-4321-8765-432187654321'), name="Property 2")
    ]
    mock_property_service.list_properties.return_value = mock_properties
    
    response = client.get('/list')
    
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['name'] == "Property 1"
    assert response.json[1]['name'] == "Property 2"

def test_create_property_missing_data(client, mock_jwt_required):
    response = client.post('/create', json={})
    
    assert response.status_code == 400
    assert response.json['error'] == "Missing property data"

def test_update_property_missing_data(client, mock_jwt_required):
    property_id = UUID('12345678-1234-5678-1234-567812345678')
    response = client.put(f'/update/{property_id}', json={})
    
    assert response.status_code == 400
    assert response.json['error'] == "Missing update data"

def test_get_nonexistent_property(client, mock_jwt_required, mock_property_service):
    property_id = UUID('12345678-1234-5678-1234-567812345678')
    mock_property_service.get_property.return_value = None
    
    response = client.get(f'/view/{property_id}')
    
    assert response.status_code == 404
    assert response.json['error'] == "Property not found"