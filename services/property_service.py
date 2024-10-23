import logging
import os
import tempfile
import time

from flask import g
from models.booking import Booking
from models.hf_message import HfMessage
from supabase_utils import supabase_client
from models.property import Property
from scraper import Scraper  # Adjust the import path if necessary
from typing import List, Optional
from uuid import UUID


class PropertyService:
    @staticmethod
    def create_property(property_data: dict) -> Property:
        try:
            property_data["owner_id"] = g.user_id
            # Insert the property into the 'properties' table
            response = (
                supabase_client.table("properties").insert(property_data).execute()
            )
            if not response.data:
                logging.error("Failed to insert property: No data returned.")
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

                logging.info(
                    f"Scraped data cleaned successfully for property {property.id}"
                )

                if scraped_data:
                    # Save the scraped data using the scraper's save method
                    filename = PropertyService.save_scraped_data(
                        str(property.id), scraped_data
                    )
                    document_data = {
                        "property_id": str(property.id),
                        "file_url": filename,
                    }
                    # Insert the document into the 'documents' table
                    document_response = (
                        supabase_client.table("documents")
                        .insert(document_data)
                        .execute()
                    )

                    log_message = (
                        f"Scraped data saved successfully for property {property.id}"
                        if filename
                        else f"Failed to save scraped data for property {property.id}"
                    )
                    (
                        logging.info(log_message)
                        if filename
                        else logging.error(log_message)
                    )
                else:
                    logging.error(f"Failed to scrape data for property {property.id}")
            else:
                logging.info(f"No 'property_url' provided for property {property.id}")
        except Exception as e:
            logging.error(f"Exception in scrape_property: {e}")
            raise

    @staticmethod
    def get_property(property_id: UUID) -> Optional[Property]:
        try:
            response = (
                supabase_client.table("properties")
                .select("*")
                .eq("id", str(property_id))
                .execute()
            )
            if not response.data:
                logging.error(f"No property found with id: {property_id}")
                return None

            return Property(**response.data[0])

        except Exception as e:
            logging.error(f"Exception in get_property: {e}")
            raise e

    @staticmethod
    def get_property_by_booking_id(booking_id: str) -> Optional[Booking]:
        try:
            response = (
                supabase_client.from_("bookings")
                .select("*")
                .eq("id", str(booking_id))
                .execute()
            )
            if not response.data:
                logging.error(f"No property found with id: {booking_id}")
                return None

            return Booking(**response.data[0])

        except Exception as e:
            logging.error(f"Exception in get_property: {e}")
            raise e

    @staticmethod
    def update_property(
        property_id: UUID, update_data: dict, user_id: UUID
    ) -> Property:
        try:
            # Verify that the user is the owner of the property
            existing_property = PropertyService.get_property(property_id)
            if not existing_property:
                raise Exception("Property not found")
            if existing_property.owner_id != user_id:
                raise Exception("Unauthorized: You do not own this property")

            response = (
                supabase_client.table("properties")
                .update(update_data)
                .eq("id", str(property_id))
                .execute()
            )
            if not response.data:
                logging.error(
                    f"Failed to update property: No data returned for property {property_id}"
                )
                raise Exception("Property not found after update")

            return Property(**response.data[0])

        except Exception as e:
            logging.error(f"Exception in update_property: {e}")
            raise e

    @staticmethod
    def delete_property(property_id: UUID, user_id: UUID) -> bool:
        try:
            # Verify that the user is the owner of the property
            existing_property = PropertyService.get_property(property_id)
            if not existing_property:
                raise Exception("Property not found")
            if existing_property.owner_id != user_id:
                raise Exception("Unauthorized: You do not own this property")

            response = (
                supabase_client.table("properties")
                .delete()
                .eq("id", str(property_id))
                .execute()
            )
            if not response.data:
                logging.error(f"Failed to delete property {property_id}")
                raise Exception(f"Failed to delete property {property_id}")

            return True
        except Exception as e:
            logging.error(f"Exception in delete_property: {e}")
            raise e

    @staticmethod
    def list_properties(owner_id: Optional[UUID] = None) -> List[Property]:
        try:
            query = supabase_client.table("properties").select("*")
            if owner_id:
                query = query.eq("owner_id", str(owner_id))

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
    def save_scraped_data(property_id, scraped_data):
        """Save scraped data as a text file to Supabase."""
        filename = f"{property_id}_{int(time.time())}.txt"
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(scraped_data.encode("utf-8"))
                temp_file_path = temp_file.name

            # Upload to Supabase
            response = supabase_client.storage.from_("properties").upload(
                filename, temp_file_path
            )

            if response:
                logging.info(f"Document uploaded successfully as {filename}")
                os.remove(temp_file_path)  # Clean up temp file
                return filename
            else:
                logging.error(f"Failed to upload document to Supabase.")
                return None
        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            return None
