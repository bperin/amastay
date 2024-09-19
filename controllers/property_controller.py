from flask import Blueprint, jsonify, request
from services.property_service import PropertyService

# Create a blueprint for PropertyController
property_bp = Blueprint('property_bp', __name__)

@property_bp.route('/properties', methods=['GET'])
def get_properties():
    """
    Handles GET request to fetch properties and returns the response in JSON format.
    """
    # Call the service to fetch properties
    properties = PropertyService.get_properties()

    # Return the properties as JSON
    if properties:
        return jsonify(properties), 200
    return jsonify({"error": "Failed to retrieve properties"}), 500

@property_bp.route('/properties/<property_id>', methods=['PUT'])
def update_property(property_id):
    """
    Handles PUT request to update a property.
    """
    # Get the data from the request
    property_data = request.get_json()

    # Call the service to update the property
    result = PropertyService.update_property(property_id, property_data)

    # Return the appropriate response
    if 'message' in result:
        return jsonify(result), 200
    return jsonify({"error": result.get('error', 'Failed to update property')}), 500

@property_bp.route('/properties/<property_id>', methods=['DELETE'])
def delete_property(property_id):
    """
    Handles DELETE request to remove a property.
    """
    # Call the service to delete the property
    result = PropertyService.delete_property(property_id)

    # Return the appropriate response
    if 'message' in result:
        return jsonify(result), 200
    return jsonify({"error": result.get('error', 'Failed to delete property')}), 500
