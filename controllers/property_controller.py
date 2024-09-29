import logging
from flask import Blueprint, request, jsonify
from models.property import Property
from services.property_service import PropertyService
from auth_utils import jwt_required
from uuid import UUID

# Create the Blueprint for property-related routes
property_bp = Blueprint("property_bp", __name__)


# Route to create a new property
@property_bp.route("/create", methods=["POST"])
@jwt_required
def create_property():
    """
    Creates a new property for the owner.
    Expects a JSON body with the property details.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing property data"}), 400

        # Create a Property model from the request data
        property_data = Property(**data)

        # Call the PropertyService to create the property
        new_property = PropertyService.create_property(property_data)

        return jsonify(new_property.dict()), 201
    except Exception as e:
        logging.error(f"Error in create_property: {e}")
        return jsonify({"error": str(e)}), 500


# Route to get a specific property by its ID
@property_bp.route("/view/<uuid:property_id>", methods=["GET"])
@jwt_required
def get_property(property_id: UUID):
    """
    Retrieves a property by its ID.
    """
    try:
        # Get the property using the PropertyService
        property_data = PropertyService.get_property(property_id)

        if not property_data:
            return jsonify({"error": "Property not found"}), 404

        return jsonify(property_data.dict()), 200
    except Exception as e:
        logging.error(f"Error in get_property: {e}")
        return jsonify({"error": str(e)}), 500


# Route to update a property
@property_bp.route("/update/<uuid:property_id>", methods=["PUT"])
@jwt_required
def update_property(property_id: UUID):
    """
    Updates a property by its ID.
    Expects a JSON body with the property updates.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing update data"}), 400

        user_id = request.headers.get("x-user-id")

        # Call the PropertyService to update the property
        updated_property = PropertyService.update_property(property_id, data, user_id)

        return jsonify(updated_property.dict()), 200
    except Exception as e:
        logging.error(f"Error in update_property: {e}")
        return jsonify({"error": str(e)}), 500


# Route to delete a property by its ID
@property_bp.route("/delete/<uuid:property_id>", methods=["DELETE"])
@jwt_required
def delete_property(property_id: UUID):
    """
    Deletes a property by its ID.
    """
    try:
        user_id = request.headers.get("x-user-id")

        # Call the PropertyService to delete the property
        success = PropertyService.delete_property(property_id, user_id)

        if success:
            return jsonify({"message": "Property deleted successfully"}), 200
        else:
            return jsonify({"error": "Failed to delete property"}), 400
    except Exception as e:
        logging.error(f"Error in delete_property: {e}")
        return jsonify({"error": str(e)}), 500


# Route to list properties for an owner (or all properties if no owner ID is provided)
@property_bp.route("/list", methods=["GET"])
@jwt_required
def list_properties():
    """
    Lists properties, optionally filtering by owner.
    """
    try:
        owner_id = request.args.get("owner_id")

        # Call the PropertyService to list properties
        properties = PropertyService.list_properties(owner_id)

        return jsonify([property.dict() for property in properties]), 200
    except Exception as e:
        logging.error(f"Error in list_properties: {e}")
        return jsonify({"error": str(e)}), 500
