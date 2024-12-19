import logging
import os
import tempfile
import time
from models.property_model import Property
from scraper import Scraper
import scraper
from services.documents_service import DocumentsService
from supabase_utils import supabase_client, supabase_admin_client
from typing import Optional


class ScraperService:
    STORAGE_BUCKET = "properties"

    @staticmethod
    async def scrape_property(property: Property) -> bool:
        """
        Scrape property data and save to storage.

        Args:
            property: Property object containing URL to scrape

        Returns:
            bool: True if scraping and saving succeeded, False otherwise

        Raises:
            ScraperError: If scraping fails
            StorageError: If saving to storage fails
        """
        try:
            if property.property_url:

                scraped_data = await Scraper().scrape(property.property_url)
                breakpoint()

                logging.info(f"Scraped data cleaned successfully for property {property.id}")

                if scraped_data:
                    # Save the scraped data using the scraper's save method
                    saved_filename = await ScraperService.save_scraped_data(property.id, scraped_data)
                    document_data = {
                        "property_id": property.id,
                        "file_id": saved_filename,
                        "primary": True,
                    }

                    # Get the full URL for the storage object
                    file_url = supabase_client.storage.from_(DocumentsService.BUCKET_NAME).get_public_url(saved_filename)
                    document_data["file_url"] = file_url

                    # Remove await from Supabase table insert since it's not async
                    document_response = supabase_client.table("documents").insert(document_data).execute()

                    log_message = f"Scraped data saved successfully for property {property.id}" if saved_filename else f"Failed to save scraped data for property {property.id}"
                    (logging.info(log_message) if saved_filename else logging.error(log_message))
                    return True
                else:
                    logging.error(f"Failed to scrape data for property {property.id}")
            else:
                logging.info(f"No 'property_url' provided for property {property.id}")
            return False
        except Exception as e:
            logging.error(f"Exception in scrape_property: {e}")
            raise

    @staticmethod
    async def save_scraped_data(property_id: str, scraped_data: str) -> Optional[str]:
        """
        Save scraped data as a text file to Supabase storage.

        Args:
            property_id: ID of the property
            scraped_data: Text data to save

        Returns:
            str: Filename if save succeeded, None if failed

        Raises:
            StorageError: If saving to storage fails
        """
        filename = f"{property_id}_{int(time.time())}.txt"
        temp_file_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as temp_file:
                temp_file.write(scraped_data)
                temp_file_path = temp_file.name

            with open(temp_file_path, "rb") as file:
                response = supabase_admin_client.storage.from_(ScraperService.STORAGE_BUCKET).upload(
                    file=file,
                    path=filename,
                    file_options={"content-type": "text/plain"},
                )

            if response:
                logging.info(f"Document uploaded successfully as {filename}")
                return filename
            logging.error(f"Failed to upload document to Supabase.")
            return None

        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            raise
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
