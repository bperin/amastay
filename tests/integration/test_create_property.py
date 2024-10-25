import unittest
from supabase_utils import create_client
import os

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class TestCreateProperty(unittest.TestCase):
    def setUp(self):
        """
        Setup method to initialize test data
        """
        self.owner_data = {
            "email_address": "owner@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "1234567890",
            "user_role": "owner",
        }
        self.property_data = {
            "property_name": "Airbnb Property Test",
            "address": "123 Airbnb St",
            "city": "Test City",
            "state": "Test State",
            "zip": "12345",
            "description": "Beautiful Airbnb property for testing AI SMS.",
        }

    def test_create_owner_and_property(self):
        """
        Test the insertion of owner and property into the database
        """
        # Insert the owner
        owner = supabase.from_("users").insert(self.owner_data).execute()
        self.assertEqual(owner.status_code, 201)

        # Insert the property
        owner_id = owner.data[0]["id"]  # Grab the inserted owner's id
        self.property_data["owner_id"] = owner_id
        property_ = supabase.from_("properties").insert(self.property_data).execute()
        self.assertEqual(property_.status_code, 201)


if __name__ == "__main__":
    unittest.main()
