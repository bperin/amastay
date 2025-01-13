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
from google.cloud import discoveryengine_v1beta
from google.cloud import storage
from services.vertex_search_service import VertexSearchService
import asyncio


class ScraperService:
    STORAGE_BUCKET = "properties"
    PROJECT_ID = "amastay"  # From service account
    LOCATION = "us-central1"  
    SEARCH_ENGINE_ID = "your-search-engine-id"  # You'll need to get this from your Vertex AI Search setup
    SERVICE_ACCOUNT_EMAIL = "vertexserviceaccount@amastay.iam.gserviceaccount.com"

    @staticmethod
    async def _update_vertex_search_index(property_id: str) -> None:
        """Updates Vertex AI search index with new property document"""
        try:
            # Initialize Vertex Search client with credentials
            client = discoveryengine_v1beta.DocumentServiceClient.from_service_account_json(
                'amastay/amastay_service_account.json'
            )
            
            # Format the parent resource name
            parent = client.branch_path(
                project=ScraperService.PROJECT_ID,
                location=ScraperService.LOCATION,
                data_store=ScraperService.SEARCH_ENGINE_ID,
                branch="default_branch"
            )

            # Create document
            document = discoveryengine_v1beta.Document(
                id=f"property_{property_id}",
                content={
                    "uri": f"gs://amastay_property_data_text/{property_id}.txt",
                    "mime_type": "text/plain"
                }
            )

            request = discoveryengine_v1beta.ImportDocumentsRequest(
                parent=parent,
                documents=[document],
                reconciliation_mode=discoveryengine_v1beta.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
            )

            operation = client.import_documents(request=request)
            result = operation.result()  # Waits for operation to complete
            
            logging.info(f"Successfully updated search index for property {property_id}")
            return result

        except Exception as e:
            logging.error(f"Failed to update Vertex search index: {e}")
            raise

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
                            destination_path = f"properties/{property.id}/{photo_id}.jpg"

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
                        doc_text = property_document.to_text()
                        # First, upload files to GCS
                        await document_service.upload_json(
                            bucket_name="amastay_property_data_json", 
                            data_list=[doc_dict], 
                            destination_path=f"{property.id}.json"
                        )

                        await document_service.upload_text(
                            bucket_name="amastay_property_data_text", 
                            text_content=doc_text, 
                            destination_path=f"{property.id}.txt"
                        )

                        # Wait a moment to ensure GCS consistency
                        await asyncio.sleep(2)

                        # Then update Vertex Search index
                        await VertexSearchService.update_property_index(property.id)

                        logging.info(f"Scraping and search index update completed for property {property.id}")

                    except Exception as e:
                        logging.error(f"Failed to process metadata: {e}")
                        raise

                   
