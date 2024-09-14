from flask import request, jsonify
from services.property_service import PropertyService

class PropertyController:
    
    @staticmethod
    def  create_property(request):
        try:
            data = request.json
            name = data.get('name')
            address = data.get('address')
            external_url = data.get('external_url')

            if not name or not address or not external_url:
                return jsonify({"error": "Missing required fields"}), 400

            new_property = PropertyService.create_property(name, address, external_url)

            if new_property:
                return jsonify(new_property), 201
            else:
                return jsonify({"error": "Failed to create property"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_properties():
        try:
            properties = PropertyService.get_properties()
            return jsonify(properties), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
