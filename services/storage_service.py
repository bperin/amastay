from google.cloud.storage import Client, Bucket, Blob
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


class StorageService:
    """Core service for Google Cloud Storage operations"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")
    BASE_BUCKET = "amastay_property_data_text"
    PHOTOS_BUCKET = "amastay_property_photos"

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_PATH)
        self.client = Client(credentials=credentials)

    async def _upload(self, bucket_name: str, file_content: Union[str, BinaryIO], destination_path: str, content_type: Optional[str] = None) -> Optional[str]:
        """Core upload method for GCS"""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_path)

            if isinstance(file_content, str):
                blob.upload_from_string(file_content)
            else:
                blob.upload_from_file(file_content)

            if content_type:
                blob.content_type = content_type

            gcs_uri = f"gs://{bucket_name}/{destination_path}"
            logging.info(f"File uploaded successfully to {gcs_uri}")
            return gcs_uri

        except Exception as e:
            logging.error(f"Error uploading file to GCS: {e}")
            raise

    async def upload_document(self, property_id: str, file_content: str, filename: str, content_type: str) -> None:
        """Upload a document to Google Cloud Storage"""
        try:
            bucket_name = "amastay_property_data_json"  # Changed from hardcoded bucket
            blob_name = f"properties/{property_id}/{filename}.{content_type.split('/')[-1]}"

            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Upload the file
            blob.upload_from_string(file_content, content_type=content_type)

            logging.info(f"File {blob_name} uploaded to {bucket_name}")

        except Exception as e:
            logging.error(f"Failed to upload document: {e}")
            raise

    async def upload_photo(self, property_id: str, photo_url: str, filename: str) -> Optional[str]:
        """Upload a photo from URL to property photos folder"""
        try:
            # Download photo
            download_service = DownloadService()
            result = await download_service.download_from_url(photo_url)
            if not result:
                return None

            content, content_type = result

            # Upload to GCS
            destination_path = f"{property_id}/{filename}"
            return await self._upload(bucket_name=self.PHOTOS_BUCKET, file_content=content, destination_path=destination_path, content_type=content_type or "image/jpeg")

        except Exception as e:
            logging.error(f"Error uploading photo from URL {photo_url}: {e}")
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
        """List all photos for a property"""
        try:
            bucket = self.client.bucket(self.PHOTOS_BUCKET)
            blobs = bucket.list_blobs(prefix=f"{property_id}/photos/")
            return [blob.name.split("/")[-1] for blob in blobs]

        except Exception as e:
            logging.error(f"Error listing photos for property {property_id}: {e}")
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

    @staticmethod
    async def store_property_data(property_id: str, data: dict) -> List[Tuple[str, str]]:
        """Store property data and return list of stored file paths."""
        stored_files = []
        logging.info(f"Starting to store property data for property {property_id}")

        try:
            # Store JSON data
            json_path = f"properties/{property_id}/data.json"
            logging.info(f"Storing JSON data at {json_path}")
            await StorageService.store_json(json_path, data)
            stored_files.append((json_path, "application/json"))
            logging.info(f"Successfully stored JSON data")

            # Store images if present
            if "images" in data:
                logging.info(f"Found {len(data['images'])} images to store")
                for idx, image_url in enumerate(data["images"]):
                    image_path = f"properties/{property_id}/images/{idx}.jpg"
                    logging.info(f"Storing image {idx + 1}/{len(data['images'])} from {image_url} to {image_path}")
                    await StorageService.store_image(image_path, image_url)
                    stored_files.append((image_path, "image/jpeg"))
                    logging.info(f"Successfully stored image {idx + 1}")

            logging.info(f"Successfully stored all property data. Total files: {len(stored_files)}")
            return stored_files

        except Exception as e:
            logging.error(f"Failed to store property data: {e}")
            if stored_files:
                logging.info("Cleaning up stored files due to error")
                for file_path, _ in stored_files:
                    logging.info(f"Deleting file: {file_path}")
                    await StorageService.delete_file(file_path)
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
