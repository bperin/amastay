from flask import request
from flask_restx import Namespace, Resource, fields
from services.model_service import ModelService

ns_model = Namespace("model", description="Model operations")

# Define input model
input_model = ns_model.model(
    "Input",
    {
        "input": fields.String(required=True, description="User input message"),
        "chat_id": fields.String(required=True, description="Unique chat identifier"),
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
    @ns_model.doc("query_model")
    @ns_model.expect(input_model)
    @ns_model.marshal_with(output_model)
    def post(self):
        """
        Query the model
        """
        try:
            data = request.json
            user_input = data.get("input")
            chat_id = data.get("chat_id")

            if not user_input or not chat_id:
                return {"error": "Input and chat_id are required"}, 400

            model_service = ModelService()
            result = model_service.query_model(
                [{"role": "user", "content": user_input}]
            )

            return {"response": result}, 200

        except Exception as e:
            ns_model.logger.error(f"Error in query_model: {str(e)}")
            return {"error": str(e)}, 500
