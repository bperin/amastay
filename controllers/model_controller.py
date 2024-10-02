from auth_utils import jwt_required
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from models.hf_message import HfMessage
from services.model_service import ModelService

ns_model = Namespace("model", description="Model operations")

# Define input model
input_model = ns_model.model(
    "Input",
    {"message": fields.String(required=True, description="User input message")},
    {"booking_id": fields.String(required=False, description="Booking ID")},
)

# Define output model
output_model = ns_model.model(
    "Output",
    {
        "response": fields.String(description="Model response"),
    },
)


model_service = ModelService()


@ns_model.route("/create_session")
class CreateSession(Resource):
    @ns_model.doc("create_session")
    @ns_model.response(201, "Session created successfully")
    @ns_model.response(500, "Internal Server Error")
    def post(self):
        """
        Create a new session for the model
        """
        try:
            session_id = model_service.create_session()

            if session_id:
                return {"session_id": session_id}, 201
            else:
                return {"error": "Failed to create session"}, 500

        except Exception as e:
            ns_model.logger.error(f"Error in create_session: {str(e)}")
            return {"error": str(e)}, 500


@ns_model.route("/query")
class QueryModel(Resource):
    @jwt_required
    @ns_model.expect(input_model)
    @ns_model.marshal_with(output_model)
    def post(self):
        """
        Query the model
        """
        try:
            data = request.json
            user_input = data.get("message")
            booking_id = data.get("booking_id")

            if not user_input or not booking_id:
                return {"error": "Both message and booking_id are required"}, 400

            result = model_service.query_model(booking_id, user_input)

            return {"response": result}, 200

        except Exception as e:
            ns_model.logger.error(f"Error in query_model: {str(e)}")
            return {"error": str(e)}, 500
