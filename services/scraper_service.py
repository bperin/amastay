import json
import logging
import os
import tempfile
import time
import uuid
import aiohttp
from models.property_document import PropertyDocument
from models.property_model import Property
from models.property_metadata_model import PropertyMetadata
from services.documents_service import DocumentsService
from services.llama_image_service import LlamaImageService
from services.storage_service import StorageService
from supabase_utils import supabase_client, supabase_admin_client
from typing import Optional
from services.photo_service import PhotoService
from services.document_service import DocumentService


class ScraperService:
    STORAGE_BUCKET = "properties"

    @staticmethod
    async def scrape_property(property: Property) -> bool:
        """
        Scrape property data using external scraper service and save to storage.

        Args:
            property: Property object containing URL to scrape

        Returns:
            bool: True if scraping and saving succeeded, False otherwise
        """
        try:
            if not property.property_url:
                logging.info(f"No 'property_url' provided for property {property.id}")
                return False

            scraper_url = f"{os.getenv('SCAPER_BASE_URL')}/scrape"
            headers = {"Authorization": f"Bearer {os.getenv('SCRAPER_AUTH_HEADER')}"}
            params = {"url": property.property_url}

            async with aiohttp.ClientSession() as session:
                async with session.get(scraper_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        logging.error(f"Scraper service returned status {response.status}")
                        return False

                    data = await response.json()

                    breakpoint()

                    # Prepare metadata for database insertion
                    metadata = {"property_id": property.id, "data": data, "scraped": True}

                    # Insert metadata into the database
                    try:
                        response = supabase_client.table("property_metadata").insert(metadata).execute()
                        if response.error:
                            logging.error(f"Failed to insert metadata into database: {response.error}")
                            return False
                        logging.info(f"Metadata inserted successfully for property {property.id}")
                    except Exception as e:
                        logging.error(f"Exception inserting metadata: {e}")
                        return False
                    logging.info(f"Scraped data cleaned successfully for property {property.id}")

                    # Save the scraped data using the scraper's save method

                    return True

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

    @staticmethod
    async def scrape_property_background(property: Property) -> None:
        """
        Background task for property scraping.
        """
        try:
            # Initialize services
            photo_service = PhotoService()
            document_service = DocumentService()

            llama_image_service = LlamaImageService()
            property_document = PropertyDocument()
            property_document.set_id(property.id)
            property_document.set_name(property.name)
            property_document.set_location(property.lat, property.lng)
            property_document.set_address(property.address)
            # Set initial progress state
            supabase_client.table("properties").update({"metadata_progress": 1}).eq("id", property.id).execute()

            # Perform the scraping
            if not property.property_url:
                logging.info(f"No 'property_url' provided for property {property.id}")
                return

            scraper_url = f"{os.getenv('SCAPER_BASE_URL')}/scrape"
            headers = {"Authorization": f"Bearer {os.getenv('SCRAPER_AUTH_HEADER')}"}
            params = {"url": property.property_url}

            async with aiohttp.ClientSession() as session:
                async with session.get(scraper_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        logging.error(f"Scraper service returned status {response.status}")
                        return

                    data = await response.json()
                    logging.info(f"Received scraper response for property {property.id}")

                    property_document.set_property_information(data["main_text"])
                    for review in data["reviews"]:
                        property_document.push_review(review)

                    for amenity in data["amenities"]:
                        property_document.push_amenity(amenity)

                    # Create metadata entry with scraped data
                    try:
                        metadata = {"property_id": property.id, "data": data, "scraped": True}
                        response = supabase_client.table("property_metadata").insert(metadata).execute()
                        if not response.data:
                            logging.error(f"Failed to insert metadata: {response.error}")
                            return
                        # Upload photos
                        for photo_url in data["photos"]:
                            photo_id = uuid.uuid4()
                            destination_path = f"properties/{property.id}/{photo_id}"

                            uploaded_url = await photo_service.upload_from_url(bucket_name="amastay_property_photos", photo_url=photo_url, destination_path=destination_path)

                            if uploaded_url:
                                logging.info(f"Photo uploaded successfully: {uploaded_url}")

                                description = llama_image_service.analyze_image(gcs_uri=f"gs://amastay_property_photos/{destination_path}")

                                # Create property photo record
                                photo_data = {"property_id": property.id, "url": photo_url, "gs_uri": f"gs://amastay_property_photos/{destination_path}", "description": description}
                                photo_response = supabase_client.table("property_photos").insert(photo_data).execute()

                                if photo_response.data:
                                    # add photo to property document
                                    property_document.push_photo(photo_data)
                                    logging.info(f"Property photo record created successfully: {photo_response.data}")
                                else:
                                    logging.error(f"Failed to create property photo record: {photo_response.error}")
                            else:
                                logging.error(f"Failed to upload photo {photo_url}")

                        metadata_id = response.data[0]["id"]
                        # Update property with metadata_id and completed progress
                        supabase_client.table("properties").update({"metadata_id": metadata_id, "metadata_progress": 2}).eq("id", property.id).execute()

                        # Upload property document
                        doc_dict = property_document.to_dict()
                        await document_service.upload_jsonl(bucket_name="amastay_property_data", data_list=[doc_dict], destination_path=f"{property.id}.jsonl")

                    except Exception as e:
                        logging.error(f"Failed to process metadata: {e}")
                        raise

                    logging.info(f"Scraping completed for property {property.id}")

        except Exception as e:
            logging.error(f"Exception in scrape_property_background: {e}")
            raise
