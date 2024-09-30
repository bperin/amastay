import os
import json
from flask import g
from sagemaker.predictor import Predictor
from sagemaker import Session


class ModelService:
    def __init__(self):
        self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        self.sagemaker_session = Session()
        self.predictor = Predictor(
            endpoint_name=self.sagemaker_endpoint,
            sagemaker_session=self.sagemaker_session,
            serializer=json.dumps,
            deserializer=json.loads,
        )

    def query_model(self, messages):
        """
        Query the SageMaker endpoint with the given messages.
        """
        try:
            payload = {"messages": messages}

            response = self.predictor.predict(payload)

            # The response structure might vary depending on your model's output
            # Adjust the following line according to the actual response structure
            return self.clean_response(response.get("generated_text", ""))

        except Exception as e:
            print(f"Error querying model: {str(e)}")
            return (
                "I apologize, but I encountered an error while processing your request."
            )

    @staticmethod
    def clean_response(response):
        """
        Clean up the response from the model.
        """
        # Remove any leading/trailing whitespace
        response = response.strip()

        # Add any other cleaning steps as needed

        return response


# Example usage:
# model_service = ModelService()
# user_input = "Who are you?"
# response = model_service.query_model(user_input)
# print("Model Response:", response)
