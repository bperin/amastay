import logging
import os
import uuid
import aiohttp
from models.property_document import PropertyDocument
from models.property_model import Property
from services.photo_service import PhotoService
from services.llama_service_vertex import LlamaService
from services.vertex_service import VertexService
from supabase_utils import supabase_client
import asyncio
from dotenv import load_dotenv
from datetime import datetime
from services.storage_service import StorageService
import json

load_dotenv()


class ScraperService:
    """Service for scraping property data"""

    @staticmethod
    async def _scrape_property_data(property_url: str) -> dict:
        """
        Fetch and process property data from scraper service
        Returns validated property data dictionary
        """
        MAX_RETRIES = 3
        RETRY_DELAY = 5  # seconds

        # Check environment variables
        scraper_base_url = os.getenv("SCRAPER_BASE_URL")
        scraper_auth = os.getenv("SCRAPER_AUTH_HEADER")

        if not scraper_base_url or not scraper_auth:
            logging.error(f"Missing environment variables. SCRAPER_BASE_URL: {scraper_base_url}, SCRAPER_AUTH_HEADER: {'present' if scraper_auth else 'missing'}")
            raise ValueError("Scraper configuration is missing. Check environment variables.")

        scraper_url = f"{scraper_base_url}/scrape"
        headers = {"Authorization": f"Bearer {scraper_auth}"}
        params = {"url": property_url}

        for attempt in range(MAX_RETRIES):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(scraper_url, headers=headers, params=params, timeout=30) as response:
                        if response.status == 503:
                            if attempt < MAX_RETRIES - 1:
                                wait_time = RETRY_DELAY * (2**attempt)
                                logging.warning(f"Scraper service busy (503), retrying in {wait_time}s (attempt {attempt + 1}/{MAX_RETRIES})")
                                await asyncio.sleep(wait_time)
                                continue
                            logging.error("Scraper service is unavailable after all retries")
                            raise ValueError("Scraper service is temporarily unavailable. Please try again later.")

                        if response.status != 200:
                            error_text = await response.text()
                            logging.error(f"Scraper service error: Status {response.status}, Response: {error_text}")
                            raise ValueError(f"Scraper service error: {response.status} - {error_text}")

                        data = await response.json()
                        logging.info(f"Received raw scraper response for URL: {property_url}")

                        # Validate required fields
                        required_fields = ["main_text", "amenities", "reviews", "photos"]
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            raise ValueError(f"Scraper response missing required fields: {missing_fields}")

                        # Process and structure the data
                        processed_data = {
                            "main_text": data["main_text"].strip(),
                            "amenities": [amenity.strip() for amenity in data["amenities"] if amenity.strip()],
                            "reviews": [review.strip() for review in data["reviews"] if review.strip()],
                            "photos": [photo.strip() for photo in data["photos"] if photo.strip() and photo.startswith("http")],
                            "metadata": {"scraped_at": datetime.now().isoformat(), "source_url": property_url, "raw_data": data},
                        }

                        # Log summary of processed data
                        logging.info(f"Processed scraper response: {len(processed_data['photos'])} photos, " f"{len(processed_data['amenities'])} amenities, " f"{len(processed_data['reviews'])} reviews")

                        return processed_data

            except aiohttp.ClientError as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2**attempt)
                    logging.warning(f"Network error, retrying in {wait_time}s (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    await asyncio.sleep(wait_time)
                    continue
                logging.error(f"Network error after all retries: {e}")
                raise ValueError(f"Failed to connect to scraper service: {e}")

    @staticmethod
    async def _process_photos(property_id: str, photos: list[str], property_document: PropertyDocument) -> None:
        """Process and upload property photos"""
        photo_service = PhotoService()
        llama_service = LlamaService()

        for photo_url in photos:
            photo_id = uuid.uuid4()
            destination_path = f"properties/{property_id}/{photo_id}.jpg"

            try:
                # Upload photo to GCS
                uploaded_url = await photo_service.upload_from_url(bucket_name="amastay_property_photos", photo_url=photo_url, destination_path=destination_path)

                if not uploaded_url:
                    logging.error(f"Failed to upload photo {photo_url}")
                    continue

                logging.info(f"Photo uploaded successfully: {uploaded_url}")

                # Get image analysis from Llama Vision
                gcs_uri = f"gs://amastay_property_photos/{destination_path}"
                description = await llama_service.analyze_image(gcs_uri=gcs_uri)
                logging.info(f"Generated description for photo: {description[:100]}...")

                # Store photo data in Supabase
                photo_data = {"property_id": property_id, "url": photo_url, "gs_uri": gcs_uri, "description": description}

                photo_response = supabase_client.table("property_photos").insert(photo_data).execute()
                if photo_response.data:
                    property_document.push_photo(photo_data)
                    logging.info(f"Property photo record created successfully")
                else:
                    logging.error(f"Failed to create property photo record: {photo_response.error}")

            except Exception as e:
                logging.error(f"Error processing photo {photo_url}: {e}")
                continue

    @staticmethod
    async def _upload_property_documents(property_id: str, property_document: PropertyDocument) -> None:
        """Upload property documents to appropriate Google Cloud Storage buckets"""
        storage_service = StorageService()
        doc_dict = property_document.to_dict()
        doc_text = property_document.to_text()

        try:
            logging.info(f"Starting document upload for property {property_id}")

            # Store text document
            logging.info("Uploading text document...")
            await storage_service.upload_document(property_id=property_id, file_content=doc_text, filename="data", content_type="text/plain")
            logging.info("Text document uploaded successfully")

            # Store JSON document
            logging.info("Uploading JSON document...")
            await storage_service.upload_document(property_id=property_id, file_content=json.dumps(doc_dict), filename="data", content_type="application/json")
            logging.info("JSON document uploaded successfully")

            logging.info(f"All documents uploaded for property {property_id}")

        except Exception as e:
            logging.error(f"Failed to upload documents for property {property_id}: {str(e)}")
            raise

    @staticmethod
    async def scrape_property_background(property: Property) -> None:
        """Background task for property scraping"""
        try:
            if not property.property_url:
                logging.info(f"No 'property_url' provided for property {property.id}")
                return

            # Initialize document and set progress
            property_document = PropertyDocument()
            property_document.set_id(property.id)
            property_document.set_name(property.name)
            property_document.set_location(property.lat, property.lng)
            property_document.set_address(property.address)

            # Set initial progress
            supabase_client.table("properties").update({"metadata_progress": 1}).eq("id", property.id).execute()

            # Fetch property data
            data = await ScraperService._scrape_property_data(property.property_url)
            logging.info(f"Received scraper response for property {property.id}")

            # Update property document
            property_document.set_property_information(data["main_text"])
            for review in data["reviews"]:
                property_document.push_review(review)
            for amenity in data["amenities"]:
                property_document.push_amenity(amenity)

            # Create metadata entry
            metadata = {"property_id": property.id, "data": data, "scraped": True}
            response = supabase_client.table("property_metadata").insert(metadata).execute()
            if not response.data:
                raise ValueError(f"Failed to insert metadata: {response.error}")

            # Process photos
            await ScraperService._process_photos(property.id, data["photos"], property_document)

            # Create or get data store ID
            data_store_id = property.data_store_id or f"property_information_{property.id}"
            if not property.data_store_id:
                await VertexService.create_data_store(property.id)
                # Update property with data store ID
                supabase_client.table("properties").update({"data_store_id": data_store_id}).eq("id", property.id).execute()

            # Update property metadata and progress
            metadata_id = response.data[0]["id"]
            supabase_client.table("properties").update({"metadata_id": metadata_id, "metadata_progress": 2, "data_store_id": data_store_id}).eq("id", property.id).execute()

            # Upload documents and update search index
            await ScraperService._upload_property_documents(property.id, property_document)

            logging.info(f"Scraping completed for property {property.id}")

        except Exception as e:
            logging.error(f"Failed to scrape property {property.id}: {e}")
            # Update property to show error state
            supabase_client.table("properties").update({"metadata_progress": -1}).eq("id", property.id).execute()
            raise
