import logging
from typing import List
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from models.property import Property
from services.property_service import PropertyService
from auth_utils import jwt_required
from uuid import UUID
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from models.property_information import PropertyInformation
from services.property_information_service import PropertyInformationService

# Create the Namespace for property-related routes
ns_property = Namespace("properties", description="Property management")

# Define models for request/response
property_model = ns_property.model(
    "Property",
    {
        "name": fields.String(required=True, description="The property name"),
        "address": fields.String(required=True, description="The property address"),
        "description": fields.String(
            required=False, description="The property description"
        ),
        "property_url": fields.String(required=True, description="The property Url"),
    },
)

# Initialize the geolocator
geolocator = Nominatim(user_agent="amastay_property_geocoder")


# Route to create a new property
@ns_property.route("/create")
class CreateProperty(Resource):
    @ns_property.doc("create_property")
    @ns_property.expect(property_model)
    @jwt_required
    def post(self):
        """
        Creates a new property for the owner and geocodes the address.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing property data"}, 400

            # Geocode the address
            address = data.get("address")
            if address:
                try:
                    # This is not a coroutine, it's a synchronous function call
                    location = geolocator.geocode(address)
                    if location:
                        data["lat"] = location.latitude
                        data["lng"] = location.longitude
                    else:
                        logging.warning(f"Failed to geocode address: {address}")
                except (GeocoderTimedOut, GeocoderServiceError) as e:
                    logging.error(f"Geocoding error: {e}")

            # Call the PropertyService to create the property
            new_property = PropertyService.create_property(data)

            return new_property.model_dump(), 201
        except ValueError as ve:
            logging.error(f"Validation error in create_property: {ve}")
            return {"error": str(ve)}, 400
        except Exception as e:
            logging.error(f"Error in create_property: {e}")
            return {"error": "An unexpected error occurred"}, 500


# Route to get a specific property by its ID
@ns_property.route("/view/<uuid:property_id>")
class ViewProperty(Resource):
    @ns_property.doc("get_property")
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

            return property_data.model_dump(), 200
        except Exception as e:
            logging.error(f"Error in get_property: {e}")
            return {"error": str(e)}, 500


# Route to update a property
@ns_property.route("/update/<uuid:property_id>")
class UpdateProperty(Resource):
    @ns_property.doc("update_property")
    @ns_property.expect(property_model)
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

            return updated_property.model_dump(), 200
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
    @jwt_required
    def get(self):
        """
        Lists properties, optionally filtering by owner.
        """
        try:
            owner_id = request.args.get("owner_id")

            # Call the PropertyService to list properties
            properties = PropertyService.list_properties(owner_id)

            return [property.model_dump() for property in properties], 200
        except Exception as e:
            logging.error(f"Error in list_properties: {e}")
            return {"error": str(e)}, 500


# Define model for property information
property_info_model = ns_property.model(
    "PropertyInformation",
    {
        "property_id": fields.String(required=True, description="Property id"),
        "name": fields.String(required=True, description="Information name"),
        "detail": fields.String(required=True, description="Information detail"),
        "video_url": fields.String(required=False, description="Information video url"),
        "category_id": fields.String(
            required=False, description="Information category_id"
        ),
    },
)


# Route to add property information
@ns_property.route("/information/")
class AddPropertyInformation(Resource):
    @ns_property.doc("add_property_information")
    @ns_property.expect(property_info_model)
    @jwt_required
    def post(self):
        """
        Adds information to a property.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing property information data"}, 400

            # Call the PropertyInformationService to add property information
            property_info = PropertyInformationService.add_property_information(data)

            return property_info.model_dump(), 201
        except Exception as e:
            logging.error(f"Error in add_property_information: {e}")
            return {"error": str(e)}, 500


# Route to remove property information
@ns_property.route("/information/<uuid:info_id>")
class RemovePropertyInformation(Resource):
    @ns_property.doc("remove_property_information")
    @jwt_required
    def delete(self, info_id: UUID):
        """
        Removes specific information from a property.
        """
        try:
            # Call the PropertyInformationService to remove property information
            success = PropertyInformationService.remove_property_information(info_id)

            if success:
                return {"message": "Property information removed successfully"}, 200
            else:
                return {"error": "Failed to remove property information"}, 400
        except Exception as e:
            logging.error(f"Error in remove_property_information: {e}")
            return {"error": str(e)}, 500


# Route to get property information by property ID
@ns_property.route("/information/<uuid:property_id>")
class GetPropertyInformation(Resource):
    @ns_property.doc("get_property_information")
    @jwt_required
    def get(self, property_id: UUID):
        """
        Get all information for a specific property.
        """
        try:
            # Call the PropertyInformationService to get property information
            property_info_list = PropertyInformationService.get_property_information(
                property_id
            )
            return [info.model_dump() for info in property_info_list], 200
        except Exception as e:
            logging.error(f"Error in get_property_information: {e}")
            return {"error": str(e)}, 500


# Route to get property by ID
@ns_property.route("/<uuid:property_id>")
class GetProperty(Resource):
    @ns_property.doc("get_property")
    @jwt_required
    def get(self, property_id: UUID):
        """
        Get a specific property by ID.
        """
        try:
            # Call the PropertyService to get the property
            property = PropertyService.get_property(property_id)
            if property:
                return property.dict(), 200
            else:
                return {"error": "Property not found"}, 404
        except Exception as e:
            logging.error(f"Error in get_property: {e}")
            return {"error": str(e)}, 500
