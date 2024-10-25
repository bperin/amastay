from auth_utils import jwt_required
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from services.guest_service import GuestService
from services.model_service import ModelService
from services.model_params_service import get_active_model_param
import logging
import pdb

from services.process_service import ProcessService

ns_model = Namespace("model", description="Model operations")

# Define input model
input_model = ns_model.model(
    "Input",
    {
        "message": fields.String(required=True, description="User input message"),
        "phone": fields.String(required=True, description="Origination number"),
    },
)

# Define output model
output_model = ns_model.model(
    "Output",
    {
        "response": fields.String(description="Model response"),
    },
)

model_service = ModelService()

# Get a logger for this module
logger = logging.getLogger(__name__)


@ns_model.route("/query")
class QueryModel(Resource):
    @jwt_required
    @ns_model.expect(input_model)
    @ns_model.marshal_with(output_model)
    def post(self):
        try:
            data = request.json
            message = data.get("message")
            phone = data.get("phone")

            # Get current model parameters
            model_params = get_active_model_param()

            result = ProcessService.handle_incoming_sms(123, phone, message)

            return result, 200  # Return the dictionary from model_service.query_model

        except Exception as e:
            logger.exception(f"Error in query_model for booking_id {phone}: {str(e)}")
            return {"error": "An unexpected error occurred"}, 500

@ns_model.route("/current")
class ModelParams(Resource):
    @jwt_required
    def get(self):
        try:
            model_params = get_active_model_param()
            return model_params.model_dump(), 200
        except Exception as e:
            logger.exception(f"Error fetching model parameters: {str(e)}")
            return {"error": "An unexpected error occurred while fetching model parameters"}, 500
