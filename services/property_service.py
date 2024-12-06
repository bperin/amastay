import logging
import os
import tempfile
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from flask import g
from models.booking import Booking
from models.document import Document
from models.hf_message import HfMessage
from services.documents_service import DocumentsService
from supabase_utils import supabase_client
from models.property import Property
from scraper import Scraper  # Adjust the import path if necessary
from typing import List, Optional, Tuple


class PropertyService:
    @staticmethod
    def geocode_address(address: str) -> Tuple[Optional[float], Optional[float]]:
        geolocator = Nominatim(user_agent="amastay_app")
        try:
            location = geolocator.geocode(address)

            if location:
                return location.latitude, location.longitude
            else:
                logging.warning(f"Could not geocode address: {address}")
                return None, None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logging.error(f"Geocoding error for address {address}: {str(e)}")
            return None, None

    @staticmethod
    def create_property(property_data: dict) -> Property:
        try:
            property_data["owner_id"] = g.user_id

            # Geocode the address
            address = property_data.get("address")
            if not address:
                raise ValueError("Address is required for property creation")

            lat, lng = PropertyService.geocode_address(address)
            if lat is None or lng is None:
                raise ValueError(f"Failed to geocode address: {address}")
            if lat and lng:
                property_data["lat"] = lat
                property_data["lng"] = lng

            # Insert the property into the 'properties' table
            response = supabase_client.table("properties").insert(property_data).execute()
            if not response.data:
                logging.error("Failed to insert property: No data returned.", response)
                raise Exception("Failed to insert property: No data returned.")

            data = response.data[0]
            new_property = Property(**data)
            PropertyService.scrape_property(new_property)
            return new_property

        except Exception as e:
            logging.error(f"Exception in create_property: {e}")
            raise

    @staticmethod
    def scrape_property(property: Property):
        try:
            if property.property_url:
                scraper = Scraper(property.property_url)
                scraped_data = scraper.scrape()

                logging.info(f"Scraped data cleaned successfully for property {property.id}")

                if scraped_data:
                    # Save the scraped data using the scraper's save method
                    filename = PropertyService.save_scraped_data(property.id, scraped_data)
                    document_data = {
                        "property_id": property.id,
                        "file_id": filename,
                    }
                    # Get the full URL for the storage object
                    file_url = supabase_client.storage.from_(DocumentsService.BUCKET_NAME).get_public_url(filename)
                    document_data["file_url"] = file_url
                    # Insert the document into the 'documents' table
                    document_response = supabase_client.table("documents").insert(document_data).execute()

                    log_message = f"Scraped data saved successfully for property {property.id}" if filename else f"Failed to save scraped data for property {property.id}"
                    (logging.info(log_message) if filename else logging.error(log_message))
                else:
                    logging.error(f"Failed to scrape data for property {property.id}")
            else:
                logging.info(f"No 'property_url' provided for property {property.id}")
        except Exception as e:
            logging.error(f"Exception in scrape_property: {e}")
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

            response = supabase_client.table("properties").delete().eq("id", str(property_id)).execute()
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
            query = supabase_client.table("properties").select("*")
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
    def save_scraped_data(property_id: str, scraped_data: str) -> str:
        """Save scraped data as a text file to Supabase."""
        filename = f"{property_id}_{int(time.time())}.txt"
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(scraped_data.encode("utf-8"))
                temp_file_path = temp_file.name

            # Upload to Supabase
            response = supabase_client.storage.from_("properties").upload(filename, temp_file_path)

            if response:
                logging.info(f"Document uploaded successfully as {filename}")
                os.remove(temp_file_path)  # Clean up temp file
                return filename
            else:
                logging.error(f"Failed to upload document to Supabase.")
                return ""
        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            return ""

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
