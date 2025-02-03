from google.cloud import storage
from google.oauth2 import service_account
import logging
import os
import tempfile
import json
import aiohttp
from typing import Optional, BinaryIO, Union, List, Dict, Any, Tuple
from pathlib import Path
from models.document_model import Document
from supabase_utils import supabase_client
from services.download_service import DownloadService
import uuid


class StorageService:
    """Core service for Google Cloud Storage operations"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")
    BASE_BUCKET = "amastay_property_data_text"
    JSON_BUCKET = "amastay_property_data_json"
    PHOTOS_BUCKET = "amastay_property_photos"

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_PATH)
        self.client = storage.Client(credentials=credentials)

    async def _upload(self, bucket_name: str, file_content: Union[str, bytes], destination_path: str, content_type: Optional[str] = None) -> Optional[str]:
        """Core upload method for GCS"""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_path)

            # Handle different content types
            if isinstance(file_content, str):
                blob.upload_from_string(file_content, content_type=content_type)
            elif isinstance(file_content, bytes):
                blob.upload_from_string(file_content, content_type=content_type)

            gcs_uri = f"gs://{bucket_name}/{destination_path}"
            logging.info(f"File uploaded successfully to {gcs_uri}")
            return gcs_uri

        except Exception as e:
            logging.error(f"Error uploading file to GCS: {e}")
            raise

    async def upload_document(self, property_id: str, file_content: str, filename: str, content_type: str) -> None:
        """Upload a document to the appropriate bucket based on content type"""
        try:
            # Select bucket based on content type
            bucket_name = self.JSON_BUCKET if content_type == "application/json" else self.BASE_BUCKET

            # Generate UUID filename with proper extension
            file_uuid = str(uuid.uuid4())
            extension = "json" if content_type == "application/json" else "txt"

            # Ensure proper path structure
            blob_name = f"properties/{property_id}/{file_uuid}.{extension}"

            # Get bucket and create if doesn't exist
            bucket = self.client.bucket(bucket_name)
            if not bucket.exists():
                bucket = self.client.create_bucket(bucket_name)
                logging.info(f"Created bucket: {bucket_name}")

            # Create and upload blob
            blob = bucket.blob(blob_name)
            blob.upload_from_string(file_content, content_type=content_type)

            # Verify upload
            if not blob.exists():
                raise Exception(f"Upload verification failed for {blob_name}")

            logging.info(f"Successfully uploaded {blob_name} to {bucket_name}")
            logging.info(f"File can be accessed at: gs://{bucket_name}/{blob_name}")

        except Exception as e:
            logging.error(f"Failed to upload document: {str(e)}")
            logging.error(f"Bucket: {bucket_name}, Blob: {blob_name}")
            logging.error(f"Content type: {content_type}")
            raise

    async def upload_photo(self, property_id: str, photo_url: str, filename: str) -> Optional[str]:
        """Upload a photo from URL to property photos folder"""
        try:
            logging.info(f"[DEBUG] StorageService: Starting photo upload from {photo_url}")

            # Download photo using download service
            download_service = DownloadService()
            result = await download_service.download_from_url(photo_url)

            if not result:
                logging.error(f"[DEBUG] StorageService: Failed to download photo from {photo_url}")
                return None

            content, content_type = result
            logging.info(f"[DEBUG] StorageService: Downloaded {len(content)} bytes with type {content_type}")

            # Upload to GCS
            destination_path = f"properties/{property_id}/{filename}"
            gcs_uri = await self._upload(bucket_name=self.PHOTOS_BUCKET, file_content=content, destination_path=destination_path, content_type=content_type or "image/jpeg")

            logging.info(f"[DEBUG] StorageService: Successfully uploaded photo to {gcs_uri}")
            return gcs_uri

        except Exception as e:
            logging.error(f"[DEBUG] StorageService: Error uploading photo: {str(e)}")
            logging.exception("[DEBUG] StorageService: Upload error traceback:")
            raise

    async def download_photo(self, property_id: str, photo_filename: str, local_path: Optional[str] = None) -> Optional[Tuple[str, bytes]]:
        """
        Download a photo from the photos bucket
        Returns tuple of (content_type, bytes) or saves to local_path if provided
        """
        try:
            bucket = self.client.bucket(self.PHOTOS_BUCKET)
            blob = bucket.blob(f"{property_id}/{photo_filename}")

            if not blob.exists():
                logging.error(f"Photo {photo_filename} not found for property {property_id}")
                return None

            if local_path:
                blob.download_to_filename(local_path)
                return local_path, blob.content_type

            # Download to memory
            content = blob.download_as_bytes()
            return blob.content_type, content

        except Exception as e:
            logging.error(f"Error downloading photo {photo_filename} for property {property_id}: {e}")
            raise

    async def list_property_photos(self, property_id: str) -> List[str]:
        """Lists all photos for a given property in GCS."""
        try:
            bucket = self.client.bucket(self.PHOTOS_BUCKET)
            prefix = f"properties/{property_id}/"

            blobs = bucket.list_blobs(prefix=prefix)
            photo_uris = [f"gs://{self.PHOTOS_BUCKET}/{blob.name}" for blob in blobs]

            return photo_uris

        except Exception as e:
            logging.error(f"Error listing property photos: {e}")
            raise

    async def download_property_photos(self, property_id: str, output_dir: str) -> List[str]:
        """Download all photos for a property to a directory"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            downloaded_files = []

            photo_files = await self.list_property_photos(property_id)
            for filename in photo_files:
                local_path = os.path.join(output_dir, filename)
                result = await self.download_photo(property_id, filename, local_path)
                if result:
                    downloaded_files.append(local_path)

            return downloaded_files

        except Exception as e:
            logging.error(f"Error downloading photos for property {property_id}: {e}")
            raise

    async def store_property_data(self, property_id: str, data: dict) -> List[Tuple[str, str]]:
        """
        Store property data and prepare for Vertex processing.
        """
        stored_files = []
        try:
            # 1. Store JSON data
            json_path = f"properties/{property_id}/data.json"
            await self._upload(bucket_name=self.JSON_BUCKET, file_content=json.dumps(data), destination_path=json_path, content_type="application/json")
            stored_files.append((json_path, "application/json"))

            # 2. Store text version for Vertex processing
            text_content = self._convert_data_to_text(data)
            text_path = f"properties/{property_id}/data.txt"
            await self._upload(bucket_name=self.BASE_BUCKET, file_content=text_content, destination_path=text_path, content_type="text/plain")
            stored_files.append((text_path, "text/plain"))

            return stored_files
        except Exception as e:
            logging.error(f"Failed to store property data: {e}")
            raise

    async def store_json(self, path: str, data: dict) -> str:
        """Store JSON data with proper content type"""
        try:
            logging.info(f"Converting data to JSON for path: {path}")
            json_content = json.dumps(data)
            logging.info(f"JSON content size: {len(json_content)} bytes")
            result = await self._upload(bucket_name=self.BASE_BUCKET, file_content=json_content, destination_path=path, content_type="application/json")
            logging.info(f"Successfully stored JSON at: {result}")
            return result
        except Exception as e:
            logging.error(f"Error storing JSON data at {path}: {e}")
            raise

    async def store_image(self, path: str, image_url: str) -> str:
        """Store image with proper content type"""
        try:
            logging.info(f"Downloading image from: {image_url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        logging.error(f"Failed to download image. Status: {response.status}")
                        raise Exception(f"Failed to download image: {response.status}")

                    content = await response.read()
                    content_type = response.headers.get("content-type", "image/jpeg")
                    logging.info(f"Downloaded image size: {len(content)} bytes, content-type: {content_type}")

                    result = await self._upload(bucket_name=self.PHOTOS_BUCKET, file_content=content, destination_path=path, content_type=content_type)
                    logging.info(f"Successfully stored image at: {result}")
                    return result
        except Exception as e:
            logging.error(f"Error storing image from {image_url} to {path}: {e}")
            raise

    def _convert_data_to_text(self, data: dict) -> str:
        """Convert property data to text format for Vertex processing"""
        text_parts = []

        if "title" in data:
            text_parts.append(f"Property: {data['title']}")
        if "description" in data:
            text_parts.append(f"Description: {data['description']}")
        if "amenities" in data:
            text_parts.append("Amenities:")
            text_parts.extend([f"- {amenity}" for amenity in data["amenities"]])
        if "location" in data:
            text_parts.append(f"Location: {data['location']}")
        if "reviews" in data:
            text_parts.append("\nReviews:")
            text_parts.extend([f"- {review}" for review in data["reviews"]])

        return "\n\n".join(text_parts)
