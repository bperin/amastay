from typing import Dict, List, Optional
from phone_utils import PhoneUtils
import logging
from models.guest import Guest
from supabase_utils import supabase_admin_client, supabase_client


class GuestService:
    """Service for managing guests"""

    @staticmethod
    def get_guest_by_phone(phone: str) -> Optional[Guest]:
        """Get a guest by phone number"""
        try:
            phone = PhoneUtils.normalize_phone(phone)
            result = supabase_client.from_("guests").select("*").eq("phone", phone).limit(1).execute()

            return Guest(**result.data[0]) if result.data else None

        except Exception as e:
            logging.error(f"Error getting guest by phone: {e}")
            raise

    @staticmethod
    def get_or_create_guest(phone: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Guest:
        """Get existing guest or create new one, updating info if needed"""
        try:
            phone = PhoneUtils.normalize_phone(phone)
            guest = GuestService.get_guest_by_phone(phone)

            if guest:
                # Check if we need to update guest information
                updates = {}
                if first_name and first_name != guest.first_name:
                    updates["first_name"] = first_name
                if last_name is not None and last_name != guest.last_name:
                    updates["last_name"] = last_name

                # If we have updates, apply them
                if updates:
                    response = supabase_admin_client.table("guests").update(updates).eq("id", guest.id).execute()
                    guest = Guest(**response.data[0])

                return guest
            else:
                # Create new guest
                guest_data = {"phone": phone, "first_name": first_name, "last_name": last_name}
                response = supabase_admin_client.table("guests").insert(guest_data).execute()
                return Guest(**response.data[0])

        except Exception as e:
            logging.error(f"Error creating/getting guest: {e}")
            raise

    @staticmethod
    def remove_guest(booking_id: str, guest_id: str) -> bool:
        """Remove a guest from a booking"""
        try:
            # TODO: Add authorization check to verify user has access to view guests for this booking
            result = supabase_client.table("booking_guests").delete().eq("booking_id", booking_id).eq("guest_id", guest_id).execute()

            return bool(result.data)

        except Exception as e:
            logging.error(f"Error removing guest: {e}")
            raise

    @staticmethod
    def get_guests_by_booking(booking_id: str) -> List[Guest]:
        """Get all guests for a booking"""
        try:
            # TODO: Add authorization check to verify user has access to view guests for this booking
            result = supabase_client.table("booking_guests").select("guests!inner(*)").eq("booking_id", booking_id).execute()

            return [Guest(**guest["guests"]) for guest in result.data] if result.data else []

        except Exception as e:
            logging.error(f"Error getting booking guests: {e}")
            raise
