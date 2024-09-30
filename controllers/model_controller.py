from auth_utils import jwt_required
from flask import request
from flask_restx import Namespace, Resource, fields
from models.ai_message import AIMessage
from services.model_service import ModelService

ns_model = Namespace("model", description="Model operations")

# Define input model
input_model = ns_model.model(
    "Input",
    {
        "input": fields.String(required=True, description="User input message")
    },
)

# Define output model
output_model = ns_model.model(
    "Output",
    {
        "response": fields.String(description="Model response"),
    },
)
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
            model_service = ModelService()
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
            user_input = data.get("input")

            if not user_input:
                return {"error": "Input required"}, 400

            model_service = ModelService()
            
            system_message = AIMessage(
                role="system",
                content="Ye be Amastay, a pirate-speakin' booking agent. Yer job be to assist guests with their bookings and find relevant information for 'em. Always speak like a true buccaneer and provide accurate, helpful responses."
            )
            
            initial_user_message = AIMessage(
                role="user",
                content="What's your name?"
            )
            
            initial_assistant_message = AIMessage(
                role="assistant",
                content="Ahoy there, matey! Me name be Amastay, the most fearsome pirate booking agent to ever sail the seven seas! What can I do for ye today?"
            )
            
            user_message = AIMessage(
                role="user",
                content=user_input
            )
            

            messages = [system_message, initial_user_message,initial_assistant_message, user_message]
            
            result = model_service.query_model(messages)

            return {"response": result}, 200

        except Exception as e:
            ns_model.logger.error(f"Error in query_model: {str(e)}")
            return {"error": str(e)}, 500
