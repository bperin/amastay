import logging
import os
import requests

# Define constants for AI and lookup integrations
AI_ENDPOINT_URL = os.getenv('AI_ENDPOINT_URL', 'http://localhost:5001/api/v1/chat')  # For AI chat processing
LOOKUP_PROPERTY_URL = os.getenv('LOOKUP_PROPERTY_URL', 'http://localhost:5001/api/v1/properties')  # For property lookup

class SMSService:

    @staticmethod
    def handle_incoming_sms(phone_number, message):
        """
        Main function to handle incoming SMS. This will decide whether the SMS
        needs to be processed as a regular chat or requires some additional lookup.
        """
        logging.info(f"Received SMS from {phone_number}: {message}")

        # Simple logic to determine whether to handle as regular chat or lookup
        if "property" in message.lower():
            logging.info("Performing property lookup...")
            return SMSService.handle_lookup_chat(phone_number, message)
        else:
            logging.info("Handling as regular chat...")
            return SMSService.handle_regular_chat(phone_number, message)

    @staticmethod
    def handle_regular_chat(phone_number, message):
        """
        Handle a regular SMS chat. This can forward messages to other participants.
        """
        logging.info(f"Processing regular chat for {phone_number}")
        
        # Forward the message to AI or participants
        ai_response = SMSService.forward_to_ai(phone_number, message)

        return {
            "status": "success",
            "ai_response": ai_response
        }

    @staticmethod
    def handle_lookup_chat(phone_number, message):
        """
        Handle an SMS chat that requires looking up property information or other details.
        """
        logging.info(f"Processing lookup chat for {phone_number}")

        # Perform a property lookup using the message content
        lookup_response = SMSService.lookup_property_info(message)

        return lookup_response

    @staticmethod
    def forward_to_ai(phone_number, message):
        """
        Forward the SMS message to the AI system and return the response.
        """
        payload = {
            "phone_number": phone_number,
            "message": message
        }

        try:
            response = requests.post(AI_ENDPOINT_URL, json=payload)
            response_data = response.json()
            logging.info(f"AI Response: {response_data}")
            return response_data
        except Exception as e:
            logging.error(f"Error forwarding to AI: {e}")
            return {"error": "Failed to communicate with AI"}

    @staticmethod
    def lookup_property_info(message):
        """
        Simulate looking up property information from a message.
        """
        # Extract property details from the message (mock logic)
        property_id = "1234"  # Mock property ID, this should be extracted from the message

        try:
            response = requests.get(f"{LOOKUP_PROPERTY_URL}/{property_id}")
            property_data = response.json()
            logging.info(f"Property lookup result: {property_data}")
            return property_data
        except Exception as e:
            logging.error(f"Error during property lookup: {e}")
            return {"error": "Failed to lookup property information"}
