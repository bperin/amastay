from google.cloud import storage
from google.oauth2 import service_account
import logging
import os
from typing import Optional, BinaryIO, Union
from pathlib import Path


class StorageService:
    """Core service for Google Cloud Storage operations"""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_PATH)
        self.client = storage.Client(credentials=credentials)

    async def upload_file(self, bucket_name: str, file_path: Union[str, BinaryIO], destination_path: str, content_type: Optional[str] = None) -> Optional[str]:
        """Upload a file to Google Cloud Storage"""
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(destination_path)

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
