import logging
from typing import List
from flask import g, request, jsonify
from flask_restx import Namespace, Resource, fields
from models.property import Property
from models.to_swagger import pydantic_to_swagger_model
from services.property_service import PropertyService
from auth_utils import jwt_required
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from models.property_information import PropertyInformation
from services.property_information_service import PropertyInformationService
from .inputs.property_inputs import get_property_input_models

# Create the Namespace for property-related routes
ns_property = Namespace("properties", description="Property management")

# Define models for request/response
property_input_models = get_property_input_models(ns_property)

create_property_model = property_input_models["create_property_model"]
update_property_model = property_input_models["update_property_model"]
add_property_info_model = property_input_models["add_property_info_model"]
update_property_info_model = property_input_models["update_property_info_model"]


property_information_response_model = pydantic_to_swagger_model(ns_property, "PropertyInformation", PropertyInformation)
property_response_model = pydantic_to_swagger_model(ns_property, "Property", Property)


# Initialize the geolocator
geolocator = Nominatim(user_agent="amastay_property_geocoder")


# Route to create a new property
@ns_property.route("/create")
class CreateProperty(Resource):
    @ns_property.doc("create_property")
    @ns_property.expect(create_property_model)
    @ns_property.response(201, "Success", property_response_model)
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


# Route to update a property
@ns_property.route("/update")
class UpdateProperty(Resource):
    @ns_property.doc("update_property")
    @ns_property.expect(update_property_model)
    @ns_property.response(200, "Success", property_response_model)
    @jwt_required
    def patch(self):
        """
        Partially updates a property by its ID.
        """
        try:
            data = request.get_json()
            property_id = data.get("id")

            if not data:
                return {"error": "Missing update data"}, 400

            # Call the PropertyService to partially update the property
            updated_property = PropertyService.update_property(property_id, data)

            return updated_property.model_dump(), 200
        except Exception as e:
            logging.error(f"Error in update_property: {e}")
            return {"error": str(e)}, 500


# Route to delete a property by its ID
@ns_property.route("/delete/<string:property_id>")
class DeleteProperty(Resource):
    @ns_property.doc("delete_property")
    @ns_property.response(204, "Property deleted")
    @jwt_required
    def delete(self, property_id: str):
        """
        Deletes a property by its ID.
        """
        try:
            user_id = g.user_id

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
    @ns_property.response(200, "Success", [property_response_model])
    @jwt_required
    def get(self):
        """
        Lists properties, optionally filtering by owner.
        """
        try:
            owner_id = g.user_id

            # Call the PropertyService to list properties
            properties = PropertyService.list_properties(owner_id)
            if len(properties) == 0:
                return [], 200
            return [property.model_dump() for property in properties], 200
        except Exception as e:
            logging.error(f"Error in list_properties: {e}")
            return {"error": str(e)}, 500


# Route to add property information
@ns_property.route("/information/")
class AddPropertyInformation(Resource):
    @ns_property.doc("add_property_information")
    @ns_property.expect(add_property_info_model)
    @ns_property.response(201, "Success", property_information_response_model)
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


# Route to get all property information
@ns_property.route("/information/<string:property_id>")
class GetAllPropertyInformation(Resource):
    @ns_property.doc("get_all_property_information")
    @ns_property.response(200, "Success", [property_information_response_model])
    @jwt_required
    def get(self, property_id: str):
        """
        Get all information for a specific property, including recommendations and categories.
        """
        try:
            # Call the PropertyInformationService to get all property information
            all_property_info = PropertyInformationService.get_property_information(property_id)

            if all_property_info is None:
                return {"error": "Property information not found"}, 404

            return [info.model_dump() for info in all_property_info], 200
        except Exception as e:
            logging.error(f"Error in get_all_property_information: {e}")
            return {"error": str(e)}, 500


# Route to remove property information
@ns_property.route("/information/delete/")
class RemovePropertyInformation(Resource):
    @ns_property.doc("remove_property_information")
    @ns_property.response(200, "Information removed")
    @jwt_required
    def post(self):
        """
        Removes specific information from a property.
        """
        try:
            data = request.get_json()
            info_id = data.get("id")
            if not info_id:
                return {"error": "Missing information ID"}, 400

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
@ns_property.route("/information/<string:property_id>")
class GetPropertyInformation(Resource):
    @ns_property.doc("get_property_information")
    @ns_property.response(200, "Success", [property_information_response_model])
    @jwt_required
    def get(self, property_id: str):
        """
        Get all information for a specific property.
        """
        try:
            # Call the PropertyInformationService to get property information
            property_info_list = PropertyInformationService.get_property_information(property_id)
            return [info.model_dump() for info in property_info_list], 200
        except Exception as e:
            logging.error(f"Error in get_property_information: {e}")
            return {"error": str(e)}, 500


# Route to update property information
@ns_property.route("/information/update")
class UpdatePropertyInformation(Resource):
    @ns_property.doc("update_property_information")
    @ns_property.expect(update_property_info_model)
    @ns_property.response(200, "Success", property_information_response_model)
    @jwt_required
    def patch(self):
        """
        Updates specific information for a property.
        """
        try:
            data = request.get_json()
            if not data:
                return {"error": "Missing update data"}, 400

            # Call the PropertyInformationService to update property information
            updated_info = PropertyInformationService.update_property_information(data)

            if updated_info:
                return updated_info.model_dump(), 200
            else:
                return {"error": "Failed to update property information"}, 400
        except ValueError as ve:
            logging.error(f"Validation error in update_property_information: {ve}")
            return {"error": str(ve)}, 400
        except Exception as e:
            logging.error(f"Error in update_property_information: {e}")
            return {"error": str(e)}, 500


# Route to get property by ID
@ns_property.route("/<string:property_id>")
class GetProperty(Resource):
    @ns_property.doc("get_property_details")
    @ns_property.response(200, "Success", property_response_model)
    @jwt_required
    def get(self, property_id: str):
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
