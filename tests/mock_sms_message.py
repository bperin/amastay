import unittest
from unittest.mock import patch
from chat_with_model import process_sms_message

class TestProcessSmsMessage(unittest.TestCase):

    @patch('chat_with_model.get_message_history')
    @patch('chat_with_model.get_renter_info')
    @patch('chat_with_model.get_property_info')
    @patch('chat_with_model.create_or_get_conversation')
    @patch('chat_with_model.invoke_model')
    def test_process_sms_message(self, mock_invoke_model, mock_create_or_get_conversation, mock_get_property_info, mock_get_renter_info, mock_get_message_history):
        # Mock conversation
        mock_create_or_get_conversation.return_value = {"id": 1}

        # Mock renter info
        mock_get_renter_info.return_value = {
            "name": "John Doe",
            "role": "Renter"
        }

        # Mock property info
        mock_get_property_info.return_value = {
            "name": "Beautiful Beach House",
            "address": "123 Ocean Ave",
            "description": "A lovely beachfront property with amazing views."
        }

        # Mock message history
        mock_get_message_history.return_value = [
            {"sender": "renter", "message": "Is there a pool?"},
            {"sender": "ai", "message": "Yes, there is a private pool."}
        ]

        # Mock model response
        mock_invoke_model.return_value = "Yes, pets are allowed."

        # Call the function with mock data
        response = process_sms_message(1, 1, "Can I bring my pet?")
        
        # Assert the AI's response
        self.assertEqual(response, "Yes, pets are allowed.")

if __name__ == '__main__':
    unittest.main()
