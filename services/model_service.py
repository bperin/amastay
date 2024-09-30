import os
import json
from typing import Optional
import boto3
from flask import g
from models.ai_message import AIMessage
from sagemaker.predictor import Predictor
from sagemaker import Session
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer  # Note the plural 'deserializers'
from models.model_response import ModelResponse, Choice, Message, Usage

class ModelService:
    def __init__(self):
        self.sagemaker_endpoint = os.getenv("SAGEMAKER_ENDPOINT")
        self.region_name = os.getenv("AWS_REGION")
        self.endpoint_url = os.getenv("SAGEMAKER_ENDPOINT_URL")
        
        # Removed sagemaker_session initialization as it's no longer needed
        self.predictor = Predictor(
            endpoint_name=self.sagemaker_endpoint,
            serializer=JSONSerializer(),
            deserializer=JSONDeserializer()
        )

    def query_model(self, messages: Optional[list[AIMessage]] = None):
        """
        Query the SageMaker endpoint with the given messages.
        """
        try:
            payload = {"messages": [message.dict() for message in messages] if messages else []}
            print(payload)
            response = self.predictor.predict(payload)
            print(response)

            model_response = ModelResponse(
                object=response['object'],
                id=response['id'],
                created=response['created'],
                model=response['model'],
                system_fingerprint=response['system_fingerprint'],
                choices=[
                    Choice(
                        index=choice['index'],
                        message=Message(
                            role=choice['message']['role'],
                            content=choice['message']['content']
                        ),
                        finish_reason=choice['finish_reason']
                    )
                    for choice in response['choices']
                ],
                usage=Usage(
                    prompt_tokens=response['usage']['prompt_tokens'],
                    completion_tokens=response['usage']['completion_tokens'],
                    total_tokens=response['usage']['total_tokens']
                )
            )

            cleaned_response = self.clean_response(model_response.choices[0].message.content)
            
            return cleaned_response

        except Exception as e:
            print(f"Error querying model: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."
    @staticmethod
    def clean_response(response):
        """
        Clean up the response from the model.
        """
        # Remove any leading/trailing whitespace
        response = response.strip()

        # Add any other cleaning steps as needed

        return response