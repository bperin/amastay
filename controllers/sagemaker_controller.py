from flask import request
from flask_restx import Namespace, Resource, fields
from auth_utils import jwt_required
from services.model_service import ModelService


# Create a Flask-RESTX Namespace
ns_sagemaker = Namespace("sagemaker", description="SageMaker endpoints for direct model access")


# Define input model
input_model = ns_sagemaker.model(
    "Input",
    {
        "input": fields.String(required=True, description="User input message"),
        "chat_id": fields.String(required=True, description="Unique chat identifier"),
    },
)

# Define output model
output_model = ns_sagemaker.model(
    "Output",
    {
        "response": fields.String(description="Model response"),
    },
)


@ns_sagemaker.route("/query_model")
class QueryModel(Resource):
    @ns_sagemaker.doc("query_model")
    @ns_sagemaker.expect(input_model)
    @ns_sagemaker.marshal_with(output_model)
    @jwt_required
    def post(self):
        """
        Queries the SageMaker model.
        """
        try:
            data = request.json
            user_input = data.get("input")
            chat_id = data.get("chat_id")

            if not user_input or not chat_id:
                return {"error": "Input and chat_id are required"}, 400

            # Query the model and get the response
            result = ModelService.query_model(user_input)

            return {"response": result}, 200

        except Exception as e:
            print(f"Error in query_model: {str(e)}")
            return {"error": str(e)}, 500
