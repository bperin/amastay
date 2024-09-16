# controllers/property_controller.py

from flask import jsonify, request
from services.property_service import PropertyService

class PropertyController:
    @staticmethod
    def get_properties():
        """
        Handles GET request to fetch properties and returns the response in JSON format.
        """
        # Call the service to fetch properties
        properties = PropertyService.get_properties()

        # Return the properties as JSON
        return jsonify(properties), 200 if 'error' not in properties else 500

    @staticmethod
    def update_property(property_id):
        """
        Handles PUT request to update a property.
        """
        # Get the data from the request
        property_data = request.get_json()

        # Call the service to update the property
        result = PropertyService.update_property(property_id, property_data)

        # Return the appropriate response
        return jsonify(result), 200 if 'message' in result else 500

    @staticmethod
    def delete_property(property_id):
        """
        Handles DELETE request to remove a property.
        """
        # Call the service to delete the property
        result = PropertyService.delete_property(property_id)

        # Return the appropriate response
        return jsonify(result), 200 if 'message' in result else 500
