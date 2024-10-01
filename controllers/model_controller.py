from auth_utils import jwt_required
from flask import request, current_app, g
from flask_restx import Namespace, Resource, fields
from models.ai_message import AIMessage
from services.model_service import ModelService
import logging

ns_model = Namespace("model", description="Model operations")

# Get the logger for this module
logger = logging.getLogger(__name__)

# Set the logging level to DEBUG for maximum verbosity
logger.setLevel(logging.DEBUG)

# We don't need to add handlers here because they are already configured in app.py
# The log messages from this module will be captured by the root logger

# Add a debug message to confirm logger configuration
logger.debug("Model controller logger configured.")


# Define input model
input_model = ns_model.model(
    "Input",
    {"message": fields.String(required=True, description="User input message")},
    {"session_id": fields.String(required=False, description="Session ID")},
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
            session_id = data.get("session_id")

            if not user_input or not session_id:
                return {"error": "Both message and session_id are required"}, 400

            result = model_service.query_model(session_id, user_input)

            return {"response": result}, 200

        except Exception as e:
            ns_model.logger.error(f"Error in query_model: {str(e)}")
            return {"error": str(e)}, 500
