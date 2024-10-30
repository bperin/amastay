import logging
from uuid import UUID
from typing import List, Optional

from flask import g
from models.property_information import PropertyInformation
from models.property import Property
from supabase_utils import supabase_client
from .property_service import PropertyService


class PropertyInformationService:
    @staticmethod
    def add_property_information(data: dict) -> PropertyInformation:
        try:
            property_id = data.get("property_id")
            if not property_id:
                raise ValueError("property_id is required for adding property information")

            # Get the property and check ownership
            property = PropertyService.get_property(property_id)
            if not property or property.owner_id != g.user_id:
                raise ValueError("Property not found or you don't have permission to add information")

            new_info_response = supabase_client.table("property_information").insert(data).execute()

            if not new_info_response.data:
                raise Exception("Failed to insert property information")

            return PropertyInformation(**new_info_response.data[0])
        except Exception as e:
            logging.error(f"Error adding property information: {e}")
            raise

    @staticmethod
    def update_property_information(data: dict) -> Optional[PropertyInformation]:
        try:
            if "id" not in data:
                raise ValueError("id is required for updating")

            id = data.pop("id")

            # Check if the property information exists
            response = supabase_client.table("property_information").select("*").eq("id", id).single().execute()
            # Marshall the property information to the actual model

            property_info = PropertyInformation(**response.data)

            property = PropertyService.get_property(property_info.property_id)
            if not property or property.owner_id != g.user_id:
                raise ValueError("You don't have permission to update this property information")

            # Create a dictionary with only the fields that can be updated
            updatable_fields = {"name": data.get("name"), "detail": data.get("detail"), "is_recommendation": data.get("is_recommendation")}

            updatable_fields = {k: v for k, v in updatable_fields.items() if v is not None}

            # Compare with current property_info and only keep changed fields
            update_data = {}
            for field, new_value in updatable_fields.items():
                current_value = getattr(property_info, field)
                if new_value != current_value:
                    update_data[field] = new_value

            # If there are no changes, return the original property_info
            if not update_data:
                return property_info

            update_response = supabase_client.table("property_information").update(update_data).eq("id", id).execute()

            if not update_response.data:
                raise Exception("Failed to update property information")

            return PropertyInformation(**update_response.data[0])
        except Exception as e:
            logging.error(f"Error updating property information: {e}")
            raise

    @staticmethod
    def remove_property_information(id: str) -> bool:
        try:
            # Find the property information
            response = supabase_client.from_("property_information").select("*").eq("id", id).single().execute()

            if not response.data:
                raise ValueError("Property information not found")

            # Marshall the response into the PropertyInformation model
            property_info = PropertyInformation(**response.data)

            # Get the property and check ownership
            property = PropertyService.get_property(property_info.property_id)
            if not property or property.owner_id != g.user_id:
                raise ValueError("You don't have permission to remove this property information")

            # Delete the property information
            delete_response = supabase_client.table("property_information").delete().eq("id", id).execute()

            if not delete_response.data:
                raise ValueError("Failed to delete property information")

            return True
        except Exception as e:
            logging.error(f"Error removing property information: {e}")
            raise

    @staticmethod
    def get_property_information(property_id: str) -> Optional[List[PropertyInformation]]:
        try:
            # Get the property and check ownership
            property = PropertyService.get_property(UUID(property_id))
            if not property or property.owner_id != g.user_id:
                raise ValueError("Property not found or you don't have permission to access this information")

            # Fetch all property information for the given property ID
            info_response = supabase_client.from_("property_information").select("*").eq("property_id", str(property_id)).execute()

            if not info_response.data:
                return None

            return [PropertyInformation(**info) for info in info_response.data]
        except Exception as e:
            logging.error(f"Error getting property information: {e}")
            raise
