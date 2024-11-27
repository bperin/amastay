from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
import phonenumbers
import logging
from supabase_utils import supabase_admin_client, supabase_client


class GuestModel(BaseModel):
    id: str
    phone: str
    email: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class GuestService:
    """Service for managing guests"""

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Normalize phone number to E.164 format without + prefix"""
        try:
            parsed = phonenumbers.parse(phone, "US")
            return str(parsed.country_code) + str(parsed.national_number)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")

    @staticmethod
    def get_guest_by_phone(phone: str) -> Optional[GuestModel]:
        """Get a guest by phone number"""
        try:
            phone = GuestService.normalize_phone(phone)
            result = supabase_client.table("guests").select("*").eq("phone", phone).limit(1).execute()

            return GuestModel(**result.data[0]) if result.data else None

        except Exception as e:
            logging.error(f"Error getting guest by phone: {e}")
            raise

    @staticmethod
    def get_or_create_guest(data: Dict) -> GuestModel:
        """Get existing guest or create new one"""
        try:
            phone = GuestService.normalize_phone(data["phone"])
            guest = GuestService.get_guest_by_phone(phone)

            if not guest:
                guest_data = {"phone": phone, "first_name": data["first_name"], "last_name": data.get("last_name")}
                response = supabase_admin_client.table("guests").insert(guest_data).execute()

                guest = GuestModel(**response.data[0])

            return guest

        except Exception as e:
            logging.error(f"Error creating/getting guest: {e}")
            raise

    @staticmethod
    def remove_guest(data: Dict) -> bool:
        """Remove a guest from a booking"""
        try:
            result = supabase_client.table("booking_guests").delete().eq("booking_id", data["booking_id"]).eq("guest_id", data["guest_id"]).execute()

            return bool(result.data)

        except Exception as e:
            logging.error(f"Error removing guest: {e}")
            raise

    @staticmethod
    def get_guests_by_booking(booking_id: str) -> List[GuestModel]:
        """Get all guests for a booking"""
        try:
            result = supabase_client.table("booking_guests").select("guests!inner(*)").eq("booking_id", booking_id).execute()

            return [GuestModel(**guest["guests"]) for guest in result.data] if result.data else []

        except Exception as e:
            logging.error(f"Error getting booking guests: {e}")
            raise
