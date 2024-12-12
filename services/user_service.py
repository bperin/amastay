from typing import Optional
import logging
from supabase_utils import supabase_client, supabase_admin_client


class UserService:
    """Service for managing user data and profile information."""

    @staticmethod
    def add_phone_number(user_id: str, phone_number: str):
        """Adds or updates phone number for a user."""
        try:
            # Validate phone number format here if needed

            # Update user's phone using admin client
            response = supabase_admin_client.auth.admin.update_user_by_id(user_id, {"phone": phone_number})
            if response.user:
                return {"message": "Phone number updated successfully"}
            else:
                return {"error": "Failed to update phone number"}

        except Exception as e:
            logging.error(f"Error updating phone number: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_user_profile(user_id: str):
        """Retrieves user profile information."""
        try:
            response = supabase_admin_client.auth.admin.get_user_by_id(user_id)
            if response.user:
                return {"id": response.user.id, "email": response.user.email, "phone": response.user.phone, "metadata": response.user.user_metadata}
            return {"error": "User not found"}
        except Exception as e:
            logging.error(f"Error retrieving user profile: {e}")
            return {"error": str(e)}

    @staticmethod
    def update_user_profile(user_id: str, update_data: dict):
        """Updates user profile information."""
        try:
            # Filter out None values and sensitive fields
            valid_fields = {k: v for k, v in update_data.items() if v is not None and k not in ["id", "email"]}

            response = supabase_admin_client.auth.admin.update_user_by_id(user_id, {"user_metadata": valid_fields})

            if response.user:
                return {"message": "Profile updated successfully"}
            return {"error": "Failed to update profile"}
        except Exception as e:
            logging.error(f"Error updating user profile: {e}")
            return {"error": str(e)}
