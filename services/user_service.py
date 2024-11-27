from typing import Optional
from flask import jsonify, make_response
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
                return make_response(jsonify({"message": "Phone number updated successfully"}), 200)
            else:
                return make_response(jsonify({"error": "Failed to update phone number"}), 400)

        except Exception as e:
            logging.error(f"Error updating phone number: {e}")
            return make_response(jsonify({"error": str(e)}), 500)

    @staticmethod
    def get_user_profile(user_id: str):
        """Retrieves user profile information."""
        try:
            response = supabase_admin_client.auth.admin.get_user_by_id(user_id)
            if response.user:
                return make_response(jsonify({"id": response.user.id, "email": response.user.email, "phone": response.user.phone, "metadata": response.user.user_metadata}), 200)
            return make_response(jsonify({"error": "User not found"}), 404)
        except Exception as e:
            logging.error(f"Error retrieving user profile: {e}")
            return make_response(jsonify({"error": str(e)}), 500)

    @staticmethod
    def update_user_profile(user_id: str, update_data: dict):
        """Updates user profile information."""
        try:
            # Filter out None values and sensitive fields
            valid_fields = {k: v for k, v in update_data.items() if v is not None and k not in ["id", "email"]}

            response = supabase_admin_client.auth.admin.update_user_by_id(user_id, {"user_metadata": valid_fields})

            if response.user:
                return make_response(jsonify({"message": "Profile updated successfully"}), 200)
            return make_response(jsonify({"error": "Failed to update profile"}), 400)
        except Exception as e:
            logging.error(f"Error updating user profile: {e}")
            return make_response(jsonify({"error": str(e)}), 500)
