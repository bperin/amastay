from models.booking import Booking
from supabase_utils import supabase_client
import json
import boto3
import os
import logging

# Load the SageMaker endpoint from environment variables
SAGEMAKER_ENDPOINT = os.getenv("SAGEMAKER_ENDPOINT")

# Initialize the SageMaker runtime client
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="us-east-1")


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
                "content": "You are an AI assistant for managing bookings. "
                f"Property information: {property_info}",
            }
        ]

        # Add the last N messages from the conversation
        for msg in messages:
            role = "user" if msg["sender_type"] == "guest" else "assistant"
            formatted_messages.append({"role": role, "content": msg["message_body"]})

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
        # Format messages into a single string
        conversation = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in messages]
        )
        payload = {"inputs": conversation}

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

            # Assuming the model returns a string directly
            return (
                model_response
                if isinstance(model_response, str)
                else str(model_response)
            )

        except Exception as e:
            logging.error(f"Error occurred while invoking the model: {str(e)}")
            return f"Error occurred: {str(e)}"
