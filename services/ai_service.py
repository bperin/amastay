from models.booking import Booking
from supabase_utils import supabase_client
import json
import boto3
import os
import logging

# Load the SageMaker endpoint from environment variables
SAGEMAKER_ENDPOINT = os.getenv("SAGEMAKER_ENDPOINT")

# Initialize the SageMaker runtime client
sagemaker_runtime = boto3.client("sagemaker-runtime")


class AIService:

    @staticmethod
    def generate_response(messages, booking: Booking):
        """
        Generates a response from the AI using the SageMaker model based on the last N messages
        and property information associated with the booking.
        """
        # Step 1: Retrieve the property information for the booking
        property_info = AIService._get_property_info(booking.property_id)

        # Step 2: Format the conversation messages for the model
        formatted_messages = [
            {
                "role": "system",
                "content": "You are an AI assistant for managing bookings.",
            }
        ]

        # Add the last N messages from the conversation
        for msg in messages:
            if msg["sender_type"] == "guest":
                formatted_messages.append(
                    {"role": "user", "content": msg["message_body"]}
                )
            elif msg["sender_type"] == "owner":
                formatted_messages.append(
                    {"role": "assistant", "content": msg["message_body"]}
                )

        # Include the property information in the context for the model
        if property_info:
            formatted_messages.append({"role": "system", "content": property_info})

        # Step 3: Query the model
        return AIService._query_model(formatted_messages)

    @staticmethod
    def _get_property_info(property_id):
        """
        Retrieves relevant property information for the given booking ID.
        Queries the 'properties_information' table to get the 'name' and 'detail'.
        """
        # Query the property information associated with the booking
        response = (
            supabase_client.table("property_information")
            .select("name, detail")
            .eq("property_id", property_id)
            .execute()
        )

        if response.data:
            # Return the concatenated property info (name and detail)
            return " ".join(
                [f"{row['name']}: {row['detail']}" for row in response.data]
            )
        else:
            return None

    @staticmethod
    def _query_model(messages):
        """
        Sends the formatted conversation to the SageMaker model and retrieves the response.
        """
        payload = {"inputs": messages}

        try:
            # Call the SageMaker endpoint
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=SAGEMAKER_ENDPOINT,
                ContentType="application/json",
                Body=json.dumps(payload),
            )

            # Decode the response body
            response_body = response["Body"].read().decode("utf-8")
            model_response = json.loads(response_body)

            # Handle response, checking if it's a list or dict
            if isinstance(model_response, list):
                return model_response[0].get("generated_text", "No response received.")
            elif isinstance(model_response, dict):
                return model_response.get("generated_text", "No response received.")
            else:
                return "Unexpected response format received."

        except Exception as e:
            logging.error(f"Error occurred while invoking the model: {str(e)}")
            return f"Error occurred: {str(e)}"
