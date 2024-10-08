from auth_utils import jwt_required
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from models.hf_message import HfMessage
from services.model_service import ModelService
import logging

ns_model = Namespace("model", description="Model operations")

# Define input model
input_model = ns_model.model(
    "Input",
    {
        "message": fields.String(required=True, description="User input message"),
        "booking_id": fields.String(required=True, description="Booking ID"),
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
                logger.info(f"Session created successfully: {session_id}")
                return {"session_id": session_id}, 201
            else:
                logger.error("Failed to create session")
                return {"error": "Failed to create session"}, 500

        except Exception as e:
            logger.exception(f"Unexpected error in create_session: {str(e)}")
            return {"error": "An unexpected error occurred"}, 500


@ns_model.route("/query")
class QueryModel(Resource):
    @jwt_required
    @ns_model.expect(input_model)
    @ns_model.marshal_with(output_model)
    def post(self):
        try:
            data = request.json
            user_input = data.get("message")
            booking_id = data.get("booking_id")

            if not user_input or not booking_id:
                logger.warning(
                    f"Invalid input: message={user_input}, booking_id={booking_id}"
                )
                return {"error": "Both message and booking_id are required"}, 400

            logger.info(f"Querying model for booking_id: {booking_id}")
            result = model_service.query_model(booking_id, user_input)

            logger.info(f"Model query successful for booking_id: {booking_id}")
            return result, 200  # Return the dictionary from model_service.query_model

        except Exception as e:
            logger.exception(
                f"Error in query_model for booking_id {booking_id}: {str(e)}"
            )
            return {"error": "An unexpected error occurred"}, 500
