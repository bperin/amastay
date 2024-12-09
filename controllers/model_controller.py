from auth_utils import jwt_required
import logging
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from services.model_params_service import get_active_model_param
from services.process_service import handle_incoming_sms
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ns_model = Namespace("model", description="Model operations")

# Define input model
input_model = ns_model.model(
    "Input",
    {
        "message": fields.String(required=True, description="User input message"),
        "phone": fields.String(required=True, description="Origination number"),
        "send_message": fields.Boolean(required=True, description="Send SMS message"),
    },
)

# Define output model
output_model = ns_model.model(
    "Output",
    {
        "response": fields.String(description="Model response"),
    },
)


@ns_model.route("/query")
class QueryModel(Resource):
    @ns_model.expect(input_model)
    def post(self):
        try:
            data = request.json
            message = data.get("message")
            phone = data.get("phone")
            message_id = str(uuid.uuid4())
            send_message = data.get("send_message", False)

            response = handle_incoming_sms(message_id, phone, message, send_message)

            return {"response": response}, 200

        except Exception as e:
            logger.exception(f"Error in query_model for phone {phone}: {str(e)}")
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
