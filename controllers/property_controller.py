from flask import request, jsonify
from services.property_service import create_property

def handle_create_property():
    """Handles the API request for creating a property."""
    data = request.get_json()

    # Get property details from the request body
    name = data.get('name')
    address = data.get('address')
    external_url = data.get('external_url')

    if not name or not address or not external_url:
        return jsonify({"error": "Missing required property information"}), 400

    # Call the service to create the property
    new_property = create_property(name, address, external_url)

    if new_property:
        return jsonify({"message": "Property created successfully", "property": new_property}), 201
    else:
        return jsonify({"error": "Failed to create property"}), 500
