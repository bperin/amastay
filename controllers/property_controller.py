import logging
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from models.property import Property
from services.property_service import PropertyService
from auth_utils import jwt_required
from uuid import UUID

# Create the Namespace for property-related routes
ns_property = Namespace("properties", description="Property management")

# Define models for request/response
property_model = ns_property.model(
    "Property",
    {
        "id": fields.String(
            readonly=True, description="The property unique identifier"
        ),
        "name": fields.String(required=True, description="The property name"),
        "address": fields.String(required=True, description="The property address"),
        "price": fields.Float(required=True, description="The property price"),
        # Add other fields as needed
    },
)


# Route to create a new property
@ns_property.route("/create")
class CreateProperty(Resource):
    @ns_property.doc("create_property")
    @ns_property.expect(property_model)
    @ns_property.marshal_with(property_model, code=201)
    @jwt_required
    def post(self):
        """
        Creates a new property for the owner.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing property data"}, 400

            # Create a Property model from the request data
            property_data = Property(**data)

            # Call the PropertyService to create the property
            new_property = PropertyService.create_property(property_data)

            return new_property.dict(), 201
        except Exception as e:
            logging.error(f"Error in create_property: {e}")
            return {"error": str(e)}, 500


# Route to get a specific property by its ID
@ns_property.route("/view/<uuid:property_id>")
class ViewProperty(Resource):
    @ns_property.doc("get_property")
    @ns_property.marshal_with(property_model)
    @jwt_required
    def get(self, property_id: UUID):
        """
        Retrieves a property by its ID.
        """
        try:
            # Get the property using the PropertyService
            property_data = PropertyService.get_property(property_id)

            if not property_data:
                return {"error": "Property not found"}, 404

            return property_data.dict(), 200
        except Exception as e:
            logging.error(f"Error in get_property: {e}")
            return {"error": str(e)}, 500


# Route to update a property
@ns_property.route("/update/<uuid:property_id>")
class UpdateProperty(Resource):
    @ns_property.doc("update_property")
    @ns_property.expect(property_model)
    @ns_property.marshal_with(property_model)
    @jwt_required
    def put(self, property_id: UUID):
        """
        Updates a property by its ID.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing update data"}, 400

            user_id = request.headers.get("x-user-id")

            # Call the PropertyService to update the property
            updated_property = PropertyService.update_property(
                property_id, data, user_id
            )

            return updated_property.dict(), 200
        except Exception as e:
            logging.error(f"Error in update_property: {e}")
            return {"error": str(e)}, 500


# Route to delete a property by its ID
@ns_property.route("/delete/<uuid:property_id>")
class DeleteProperty(Resource):
    @ns_property.doc("delete_property")
    @jwt_required
    def delete(self, property_id: UUID):
        """
        Deletes a property by its ID.
        """
        try:
            user_id = request.headers.get("x-user-id")

            # Call the PropertyService to delete the property
            success = PropertyService.delete_property(property_id, user_id)

            if success:
                return {"message": "Property deleted successfully"}, 200
            else:
                return {"error": "Failed to delete property"}, 400
        except Exception as e:
            logging.error(f"Error in delete_property: {e}")
            return {"error": str(e)}, 500


# Route to list properties for an owner (or all properties if no owner ID is provided)
@ns_property.route("/list")
class ListProperties(Resource):
    @ns_property.doc("list_properties")
    @ns_property.marshal_list_with(property_model)
    @jwt_required
    def get(self):
        """
        Lists properties, optionally filtering by owner.
        """
        try:
            owner_id = request.args.get("owner_id")

            # Call the PropertyService to list properties
            properties = PropertyService.list_properties(owner_id)

            return [property.dict() for property in properties], 200
        except Exception as e:
            logging.error(f"Error in list_properties: {e}")
            return {"error": str(e)}, 500
