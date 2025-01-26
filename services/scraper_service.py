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
from services.llama_image_service import LlamaImageService

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
        try:
            logging.info(f"[DEBUG] Starting _process_photos with {len(photos)} photos for property {property_id}")
            logging.info(f"[DEBUG] Photo URLs: {photos[:3]}...")  # Log first 3 photos

            storage_service = StorageService()

            for index, photo_url in enumerate(photos):
                try:
                    logging.info(f"[DEBUG] Processing photo {index + 1}/{len(photos)}")
                    logging.info(f"[DEBUG] Photo URL: {photo_url}")

                    # Generate unique filename
                    photo_uuid = str(uuid.uuid4())
                    filename = f"{photo_uuid}.jpg"
                    logging.info(f"[DEBUG] Generated filename: {filename}")

                    # First: Download and upload photo to GCS
                    logging.info(f"[DEBUG] Downloading and uploading photo...")
                    uploaded_url = await storage_service.upload_photo(property_id=property_id, photo_url=photo_url, filename=filename)

                    if not uploaded_url:
                        logging.error(f"[DEBUG] Failed to upload photo {photo_url}")
                        continue

                    logging.info(f"[DEBUG] Photo uploaded successfully: {uploaded_url}")

                    # Second: Now that photo is in GCS, analyze it with Llama
                    gcs_uri = f"gs://{storage_service.PHOTOS_BUCKET}/properties/{property_id}/{filename}"
                    logging.info(f"[DEBUG] Getting Llama image analysis for {gcs_uri}")
                    description = await LlamaImageService.analyze_image(gcs_uri=gcs_uri)
                    logging.info(f"[DEBUG] Generated description: {description[:100]}...")

                    # Add photo with description to property document
                    photo_data = {"url": photo_url, "gs_uri": gcs_uri, "filename": filename, "description": description}
                    property_document.push_photo(photo_data)
                    logging.info(f"[DEBUG] Added photo with description to property document")

                except Exception as e:
                    logging.error(f"[DEBUG] Error processing individual photo {photo_url}: {str(e)}")
                    logging.exception("[DEBUG] Photo processing error traceback:")
                    continue

            logging.info(f"[DEBUG] Completed processing all photos for property {property_id}")

        except Exception as e:
            logging.error(f"[DEBUG] Error in _process_photos: {str(e)}")
            logging.exception("[DEBUG] Full traceback:")
            raise

    @staticmethod
    async def _upload_property_documents(property_id: str, property_document: PropertyDocument) -> None:
        """Upload property documents to appropriate Google Cloud Storage buckets"""
        try:
            logging.info(f"[DEBUG] Starting _upload_property_documents for property {property_id}")
            storage_service = StorageService()

            doc_dict = property_document.to_dict()
            doc_text = property_document.to_text()

            logging.info(f"[DEBUG] Document text length: {len(doc_text)}")
            logging.info(f"[DEBUG] Document JSON keys: {doc_dict.keys()}")

            # Store text document in BASE_BUCKET
            logging.info("[DEBUG] Uploading text document...")
            await storage_service.upload_document(property_id=property_id, file_content=doc_text, filename="data", content_type="text/plain")
            logging.info("[DEBUG] Text document uploaded successfully")

            # Store JSON document in JSON_BUCKET
            logging.info("[DEBUG] Uploading JSON document...")
            await storage_service.upload_document(property_id=property_id, file_content=json.dumps(doc_dict), filename="data", content_type="application/json")
            logging.info("[DEBUG] JSON document uploaded successfully")
            logging.info(f"[DEBUG] _upload_property_documents completed for property {property_id}")

        except Exception as e:
            logging.error(f"[DEBUG] Failed in _upload_property_documents: {str(e)}")
            logging.exception("Full traceback:")
            raise

    @staticmethod
    async def scrape_property_background(property: Property) -> None:
        """Background task for property scraping"""
        try:
            logging.info(f"[DEBUG] Starting scrape_property_background for property {property.id}")

            if not property.property_url:
                logging.info(f"[DEBUG] No 'property_url' provided for property {property.id}")
                return

            # Initialize document
            property_document = PropertyDocument()
            property_document.set_id(property.id)
            property_document.set_name(property.name)
            property_document.set_location(property.lat, property.lng)
            property_document.set_address(property.address)

            logging.info(f"[DEBUG] Property document initialized for {property.id}")

            # Set initial progress
            supabase_client.table("properties").update({"metadata_progress": 1}).eq("id", property.id).execute()
            logging.info("[DEBUG] Initial progress set")

            # Fetch and process data
            data = await ScraperService._scrape_property_data(property.property_url)
            logging.info(f"[DEBUG] Property data fetched for {property.id}")

            # After fetching data
            logging.info(f"[DEBUG] Raw photos data: {data.get('photos', [])}")
            logging.info(f"[DEBUG] Scraped data photos array length: {len(data.get('photos', []))}")
            if data.get("photos"):
                logging.info(f"[DEBUG] First few photo URLs: {data['photos'][:3]}")
                logging.info("[DEBUG] Starting photo processing")
                try:
                    await ScraperService._process_photos(property.id, data["photos"], property_document)
                    logging.info("[DEBUG] Photo processing completed")
                except Exception as e:
                    logging.error(f"[DEBUG] Error during photo processing: {str(e)}")
                    logging.exception("[DEBUG] Photo processing error traceback:")
                    raise
            else:
                logging.warning("[DEBUG] No photos found in scraped data")

            # Update document
            property_document.set_property_information(data["main_text"])
            for review in data["reviews"]:
                property_document.push_review(review)
            for amenity in data["amenities"]:
                property_document.push_amenity(amenity)
            logging.info("[DEBUG] Property document updated with scraped data")

            # Upload documents
            logging.info("[DEBUG] Starting document upload")
            await ScraperService._upload_property_documents(property.id, property_document)
            logging.info("[DEBUG] Document upload completed")

            logging.info(f"[DEBUG] Scraping completed for property {property.id}")

        except Exception as e:
            logging.error(f"[DEBUG] Error in scrape_property_background: {str(e)}")
            logging.exception("Full traceback:")
            raise
