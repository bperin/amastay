from auth_utils import jwt_required
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from services.model_params_service import get_active_model_param
from services.process_service import handle_incoming_sms


ns_model = Namespace("model", description="Model operations")

# Define input model
input_model = ns_model.model(
    "Input",
    {
        "message": fields.String(required=True, description="User input message"),
        "phone": fields.String(required=True, description="Origination number"),
        "message_id": fields.String(required=True, description="Message id"),
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
    @jwt_required
    @ns_model.expect(input_model)
    def post(self):
        try:
            data = request.json
            message = data.get("message")
            phone = data.get("phone")
            message_id = data.get("message_id")

            handle_incoming_sms(message_id, phone, message)

            return {"status": "success"}, 200

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
