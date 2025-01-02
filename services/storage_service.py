from google.cloud import storage
from google.oauth2 import service_account
import logging
import json
import tempfile
import os
from typing import Optional, BinaryIO, Union, Dict, Any
from pathlib import Path
import aiohttp


class StorageService:
    """Service for handling Google Cloud Storage operations"""

    # Service account path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")

    def __init__(self):
        """Initialize the Google Cloud Storage client"""
        credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_PATH)
        self.client = storage.Client(credentials=credentials)

    async def upload_file(self, bucket_name: str, file_path: Union[str, BinaryIO], destination_path: str, content_type: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Cloud Storage.

        Args:
            bucket_name: Name of the GCS bucket
            file_path: Path to file or file-like object to upload
            destination_path: Path where file will be stored in bucket
            content_type: MIME type of the file (optional)

        Returns:
            str: Public URL of uploaded file if successful, None if failed
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_path)

            # Handle both file paths and file-like objects
            if isinstance(file_path, (str, Path)):
                blob.upload_from_filename(file_path)
            else:
                blob.upload_from_file(file_path)

            if content_type:
                blob.content_type = content_type

            logging.info(f"File uploaded successfully to {destination_path}")
            return blob.public_url

        except Exception as e:
            logging.error(f"Error uploading file to GCS: {e}")
            raise

    async def upload_json(self, bucket_name: str, data: Dict[str, Any], destination_path: str) -> Optional[str]:
        """
        Upload JSON data to Google Cloud Storage.

        Args:
            bucket_name: Name of the GCS bucket
            data: Dictionary to be stored as JSON
            destination_path: Path where file will be stored in bucket

        Returns:
            str: Public URL of uploaded file if successful, None if failed
        """
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                json.dump(data, temp_file)
                temp_path = temp_file.name

            return await self.upload_file(bucket_name=bucket_name, file_path=temp_path, destination_path=destination_path, content_type="application/json")

        finally:
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

    async def upload_jsonl(self, bucket_name: str, data_list: list[Dict[str, Any]], destination_path: str) -> Optional[str]:
        """
        Upload data as JSONL (JSON Lines) to Google Cloud Storage.

        Args:
            bucket_name: Name of the GCS bucket
            data_list: List of dictionaries to be stored as JSONL
            destination_path: Path where file will be stored in bucket

        Returns:
            str: Public URL of uploaded file if successful, None if failed
        """
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                for item in data_list:
                    temp_file.write(json.dumps(item) + "\n")
                temp_path = temp_file.name

            return await self.upload_file(bucket_name=bucket_name, file_path=temp_path, destination_path=destination_path, content_type="application/x-jsonlines")

        finally:
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

    async def upload_photo(self, bucket_name: str, photo_data: Union[str, BinaryIO], destination_path: str, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Upload a photo to Google Cloud Storage.

        Args:
            bucket_name: Name of the GCS bucket
            photo_data: Path to photo file or file-like object
            destination_path: Path where file will be stored in bucket
            content_type: MIME type of the image (default: image/jpeg)

        Returns:
            str: Public URL of uploaded photo if successful, None if failed
        """
        return await self.upload_file(bucket_name=bucket_name, file_path=photo_data, destination_path=destination_path, content_type=content_type)

    async def upload_photo_from_url(self, bucket_name: str, photo_url: str, destination_path: str, content_type: str = "image/jpeg") -> Optional[str]:
        """
        Download photo from URL and upload to Google Cloud Storage.

        Args:
            bucket_name: Name of the GCS bucket
            photo_url: URL of the photo to download
            destination_path: Path where file will be stored in bucket
            content_type: MIME type of the image (default: image/jpeg)

        Returns:
            str: Public URL of uploaded photo if successful, None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(photo_url) as response:
                    if response.status != 200:
                        logging.error(f"Failed to download photo from {photo_url}")
                        return None

                    # Save to temp file
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(await response.read())
                        temp_path = temp_file.name

                    try:
                        return await self.upload_file(bucket_name=bucket_name, file_path=temp_path, destination_path=destination_path, content_type=content_type)
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

        except Exception as e:
            logging.error(f"Error uploading photo from URL {photo_url}: {e}")
            raise
