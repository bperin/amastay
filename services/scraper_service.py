import logging
import os
import uuid
import aiohttp
from models.property_document import PropertyDocument
from models.property_model import Property
from services.photo_service import PhotoService
from services.document_service import DocumentService
from services.llama_image_service import LlamaImageService
from services.vertex_service import VertexService
from supabase_utils import supabase_client
import asyncio
from dotenv import load_dotenv

load_dotenv()


class ScraperService:
    """Service for scraping property data"""

    @staticmethod
    async def _scrape_property_data(property_url: str) -> dict:
        """Fetch property data from scraper service"""
        MAX_RETRIES = 3
        RETRY_DELAY = 5  # seconds

        # Check environment variables
        scraper_base_url = os.getenv("SCRAPER_BASE_URL")
        print(scraper_base_url)
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

                        return await response.json()

            except aiohttp.ClientError as e:
                if attempt < MAX_RETRIES - 1:
                    wait_time = RETRY_DELAY * (2**attempt)
                    logging.warning(f"Network error, retrying in {wait_time}s (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                    await asyncio.sleep(wait_time)
                    continue
                logging.error(f"Network error after all retries: {e}")
                raise ValueError(f"Failed to connect to scraper service: {e}")
            except Exception as e:
                logging.error(f"Unexpected error in scraper: {e}")
                raise

    @staticmethod
    async def _process_photos(property_id: str, photos: list[str], property_document: PropertyDocument) -> None:
        """Process and upload property photos"""

        photo_service = PhotoService()
        llama_image_service = LlamaImageService()

        for photo_url in photos:
            photo_id = uuid.uuid4()
            destination_path = f"properties/{property_id}/{photo_id}.jpg"

            try:
                uploaded_url = await photo_service.upload_from_url(bucket_name="amastay_property_photos", photo_url=photo_url, destination_path=destination_path)

                if not uploaded_url:
                    logging.error(f"Failed to upload photo {photo_url}")
                    continue

                logging.info(f"Photo uploaded successfully: {uploaded_url}")
                description = llama_image_service.analyze_image(gcs_uri=f"gs://amastay_property_photos/{destination_path}")

                photo_data = {"property_id": property_id, "url": photo_url, "gs_uri": f"gs://amastay_property_photos/{destination_path}", "description": description}

                photo_response = supabase_client.table("property_photos").insert(photo_data).execute()
                if photo_response.data:
                    property_document.push_photo(photo_data)

                    logging.info(f"Property photo record created successfully: {photo_response.data}")
                else:
                    logging.error(f"Failed to create property photo record: {photo_response.error}")

            except Exception as e:
                logging.error(f"Error processing photo {photo_url}: {e}")

    @staticmethod
    async def _upload_property_documents(property_id: str, property_document: PropertyDocument) -> None:
        """Upload property documents to storage and update search index"""
        document_service = DocumentService()
        doc_dict = property_document.to_dict()
        doc_text = property_document.to_text()

        try:
            # Upload text version to GCS
            text_bucket = "amastay_property_data_text"
            text_path = f"{property_id}.txt"
            await document_service.upload_text(bucket_name=text_bucket, text_content=doc_text, destination_path=text_path)

            # Wait for GCS consistency
            await asyncio.sleep(2)

            # Import document into Vertex AI Search
            data_store_id = f"property_information_{property_id}"
            gcs_uri = f"gs://{text_bucket}/{text_path}"

            # Create data store for this property if it doesn't exist
            # await VertexService.create_data_store(property_id)

            # Import the document into the data store
            await VertexService.import_documents(data_store_id=data_store_id, gcs_uri=gcs_uri)

            logging.info(f"Documents uploaded and imported for property {property_id}")

        except Exception as e:
            logging.error(f"Failed to upload/import documents: {e}")
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

            # Update property metadata
            metadata_id = response.data[0]["id"]
            supabase_client.table("properties").update({"metadata_id": metadata_id, "metadata_progress": 2}).eq("id", property.id).execute()

            # Upload documents and update search index
            await ScraperService._upload_property_documents(property.id, property_document)

            logging.info(f"Scraping completed for property {property.id}")

        except Exception as e:
            logging.error(f"Failed to scrape property {property.id}: {e}")
            # Update property to show error state
            supabase_client.table("properties").update({"metadata_progress": -1}).eq("id", property.id).execute()
            raise
