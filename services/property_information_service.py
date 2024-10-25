import logging
from uuid import UUID
from typing import List, Optional

from flask import g
from models.property_information import PropertyInformation
from models.property import Property
from supabase_utils import supabase_client


class PropertyInformationService:
    @staticmethod
    def add_property_information(data: dict) -> PropertyInformation:
        try:
            # Check if the property exists and belongs to the user
            property_response = (
                supabase_client.table("properties")
                .select("*")
                .eq("id", str(data["property_id"]))
                # .eq("owner_id", g.user_id)
                .execute()
            )

            if not property_response.data:
                raise ValueError("Property not found or you don't have permission to add information")

            new_info_response = supabase_client.table("property_information").insert(data).execute()

            if not new_info_response.data:
                raise Exception("Failed to insert property information")

            return PropertyInformation(**new_info_response.data[0])
        except Exception as e:
            logging.error(f"Error adding property information: {e}")
            raise

    @staticmethod
    def remove_property_information(info_id: UUID) -> bool:
        try:
            # Find and delete the property information
            delete_response = supabase_client.table("property_information").delete().eq("id", str(info_id)).execute()

            if not delete_response.data:
                raise ValueError("Property information not found")

            return True
        except Exception as e:
            logging.error(f"Error removing property information: {e}")
            raise

    @staticmethod
    def get_property_information(
        property_id: str,
    ) -> Optional[List[PropertyInformation]]:
        try:
            # Fetch all property information for the given property ID
            info_response = supabase_client.from_("property_information").select("*").eq("property_id", str(property_id)).execute()

            if not info_response.data:
                return None

            return [PropertyInformation(**info) for info in info_response.data]
        except Exception as e:
            logging.error(f"Error getting property information: {e}")
            raise
