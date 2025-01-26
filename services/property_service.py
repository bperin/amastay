import logging
from uuid import UUID
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from models.manager_model import Manager
from models.owner_model import Owner
from models.property_photo_model import PropertyPhoto
from supabase_utils import supabase_client
from models.property_model import CreateProperty, Property
from typing import List, Optional, Tuple
from urllib.parse import urlparse, urlunparse
from .vertex_service import VertexService
from .storage_service import StorageService
from datetime import datetime


class PropertyService:
    @staticmethod
    def geocode_address(address: str) -> Tuple[Optional[str], Optional[float], Optional[float]]:
        """
        Geocode and normalize an address.

        Args:
            address: Raw address string

        Returns:
            Tuple containing (normalized_address, latitude, longitude)
            Returns (None, None, None) if geocoding fails
        """
        geolocator = Nominatim(user_agent="amastay_app")
        try:
            location = geolocator.geocode(address)

            if location:
                return location.address, location.latitude, location.longitude
            else:
                logging.warning(f"Could not geocode address: {address}")
                return None, None, None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logging.error(f"Geocoding error for address {address}: {str(e)}")
            return None, None, None

    @staticmethod
    def clean_url(url: str) -> str:
        """Clean URL by removing query parameters"""
        if not url:
            return url
        return url.split("?")[0].rstrip("/")

    @staticmethod
    async def create_property(create_property_request: CreateProperty, owner_id: str) -> Property:
        try:
            # Clean the property URL before saving
            if create_property_request.property_url:
                create_property_request.property_url = PropertyService.clean_url(create_property_request.property_url)

            create_property_data = create_property_request.model_dump()
            create_property_data["owner_id"] = owner_id

            # Geocode the address
            address = create_property_request.address
            if not address:
                raise ValueError("Address is required for property creation")

            normalized_address, lat, lng = PropertyService.geocode_address(address)

            if lat is None or lng is None:
                raise ValueError(f"Failed to geocode address: {address}")
            if lat and lng:
                create_property_data["lat"] = lat
                create_property_data["lng"] = lng

            if normalized_address:
                create_property_data["address"] = normalized_address

            create_property_data["manager_id"] = None

            response = supabase_client.table("properties").insert(create_property_data).execute()

            if not response.data:
                logging.error("failed to create property")
                raise ("failed to create property")

            return Property(**response.data[0])

        except Exception as e:
            logging.error(f"Exception in create_property: {e}")
            raise

    @staticmethod
    def get_property(id: str) -> Optional[Property]:
        try:
            response = supabase_client.table("properties").select("*").eq("id", id).single().execute()
            if not response.data:
                logging.error(f"No property found with id: {id}")
                return None

            return Property(**response.data)

        except Exception as e:
            logging.error(f"Exception in get_property: {e}")
            raise e

    @staticmethod
    def get_property_by_booking_id(property_id: str) -> Optional[Property]:
        try:
            response = supabase_client.from_("properties").select("*").eq("id", str(property_id)).execute()
            if not response.data:
                logging.error(f"No property found with id: {property_id}")
                return None

            return Property(**response.data[0])

        except Exception as e:
            logging.error(f"Exception in get_property: {e}")
            raise e

    @staticmethod
    def update_property(property_id: str, update_data: dict) -> Property:
        try:

            # Verify that the user is the owner of the property
            existing_property = PropertyService.get_property(property_id)
            if not existing_property:
                raise Exception("Property not found")
            if existing_property.owner_id != g.user_id:
                raise Exception("Unauthorized: You do not own this property")

            # Only update fields that are different from the existing property
            fields_to_update = {}
            for key, value in update_data.items():
                if hasattr(existing_property, key) and getattr(existing_property, key) != value:
                    fields_to_update[key] = value

            # If address is updated, re-geocode
            if "address" in fields_to_update:
                address = fields_to_update["address"]
                lat, lng = PropertyService.geocode_address(address)
                if lat and lng:
                    fields_to_update["lat"] = lat
                    fields_to_update["lng"] = lng

            rescrape_needed = False
            if "property_url" in fields_to_update and fields_to_update["property_url"] != existing_property.property_url:
                rescrape_needed = True
                # Delete existing documents for this property
                supabase_client.table("documents").delete().eq("property_id", existing_property.id).execute()

            if not fields_to_update:
                return existing_property  # No changes needed

            response = supabase_client.table("properties").update(fields_to_update).eq("id", existing_property.id).execute()

            if not response.data:
                logging.error(f"Failed to update property: No data returned for property {property_id}")
                raise Exception("Property not found after update")

            udpated_property = Property(**response.data[0])
            if rescrape_needed:
                PropertyService.scrape_property(udpated_property)
            return udpated_property

        except Exception as e:
            logging.error(f"Exception in update_property: {e}")
            raise e

    @staticmethod
    def delete_property(property_id: str, user_id: str) -> bool:
        try:
            # Verify that the user is the owner of the property
            existing_property = PropertyService.get_property(property_id)
            if not existing_property:
                raise Exception("Property not found")
            if existing_property.owner_id != user_id:
                raise Exception("Unauthorized: You do not own this property")

            response = supabase_client.table("properties").delete().eq("id", property_id).execute()
            if not response.data:
                logging.error(f"Failed to delete property {property_id}")
                raise Exception(f"Failed to delete property {property_id}")

            return True
        except Exception as e:
            logging.error(f"Exception in delete_property: {e}")
            raise e

    @staticmethod
    def list_properties(owner_id: str) -> List[Property]:
        try:
            query = supabase_client.from_("properties").select("*").order("created_at", desc=True)
            if owner_id:
                query = query.eq("owner_id", owner_id)

            response = query.execute()
            if not response.data:
                logging.error("No properties found")
                return []

            properties = [Property(**prop) for prop in response.data]
            return properties
        except Exception as e:
            logging.error(f"Exception in list_properties: {e}")
            raise e

    @staticmethod
    def assign_manager(*, property_id: str, manager_id: str) -> Optional[Property]:
        """
        Assigns a manager to a property.

        Args:
            property_id: str of the property to update
            manager_id: str of the manager to assign

        Returns:
            Optional[Property]: The updated property if successful, None if property not found
        """
        try:
            # Verify manager exists
            manager_check = supabase_client.table("managers").select("*").eq("id", manager_id).execute()
            if not manager_check.data:
                raise ValueError(f"Manager with ID {manager_id} not found")

            # Update property with new manager
            response = supabase_client.table("properties").update({"manager_id": manager_id}).eq("id", property_id).execute()

            if not response.data:
                return None

            return Property(**response.data[0])
        except Exception as e:
            logging.error(f"Error assigning manager {manager_id} to property {property_id}: {e}")
            raise

    @staticmethod
    def get_property_details(property_id: str) -> Optional[Property]:
        """
        Get property details including owner and manager relationships.

        Args:
            property_id: UUID of the property

        Returns:
            Property object with owner and manager relationships populated
        """
        try:
            response = (
                supabase_client.from_("properties")
                .select(
                    """
                    *,
                    owner:owners(*),
                    manager:managers(*)
                """
                )
                .eq("id", property_id)
                .single()
                .execute()
            )

            if not response.data:
                logging.error(f"No property found with id: {property_id}")
                return None

            # Convert to Property model and include relationships
            property_data = response.data

            # Create base property object
            property = Property(**{k: v for k, v in property_data.items() if k not in ["owner", "manager"]})

            # Add relationships if they exist
            if "owner" in property_data and property_data["owner"]:
                property.owner = Owner(**property_data["owner"])

            if "manager" in property_data and property_data["manager"]:
                property.manager = Manager(**property_data["manager"])

            return property

        except Exception as e:
            logging.error(f"Exception in get_property_details: {e}")
            raise e

    @staticmethod
    def get_property_photos(property_id: str) -> list[PropertyPhoto]:
        """
        Get all photos for a property.

        Args:
            property_id: UUID of the property

        Returns:
            List of PropertyPhoto objects
        """
        try:
            response = supabase_client.from_("property_photos").select("*").eq("property_id", property_id).order("created_at", desc=True).execute()

            if not response.data:
                return []

            return [PropertyPhoto(**photo) for photo in response.data]

        except Exception as e:
            logging.error(f"Exception in get_property_photos: {property_id}: {e}")
            raise e

    @staticmethod
    async def update_property_data_store(property_id: str, data_store_id: str) -> Property:
        """Update property with data store ID"""
        try:
            response = supabase_client.from_("properties").update({"data_store_id": data_store_id}).eq("id", property_id).execute()

            if not response.data:
                raise ValueError(f"Failed to update property {property_id} with data store ID")

            return Property(**response.data[0])
        except Exception as e:
            logging.error(f"Error updating property data store: {e}")
            raise

    @staticmethod
    async def scrape_and_index_property(property_id: str, user_id: str):
        """Scrape property data and index it in vertex search."""
        try:
            # Get property details
            property = PropertyService.get_property(property_id)

            # Create data store ID if not exists
            data_store_id = property.data_store_id or f"property_information_{property_id}"
            if not property.data_store_id:
                await VertexService.create_data_store(property_id)
                await PropertyService.update_property_data_store(property_id, data_store_id)

            # Scrape the property
            scrape_result = await PropertyService.scrape_property(property_id)

            # Store scraped data with content types
            stored_files = await StorageService.store_property_data(property_id=property_id, data=scrape_result.data)

            # Index in vertex search with data store ID
            await VertexService.index_property(property_id=property_id, property_data=scrape_result.data, files=stored_files, data_store_id=data_store_id)  # Now contains tuples of (path, content_type)

            # Update property status
            PropertyService.update_property(property_id=property_id, update_data={"last_scraped_at": datetime.now(), "scrape_status": "completed"})

        except Exception as e:
            logger.error(f"Failed to scrape and index property {property_id}: {e}")
            PropertyService.update_property(property_id=property_id, update_data={"scrape_status": "failed", "scrape_error": str(e)})
            raise
