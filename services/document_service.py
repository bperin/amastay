import json
import logging
import os
import tempfile
from typing import Optional, Dict, Any
from services.storage_service import StorageService
import google.cloud.storage as storage


class DocumentService:
    """Service for handling document operations"""

    def __init__(self):
        self.storage_service = StorageService()

    async def upload_json(self, bucket_name: str, data_list: list[Dict[str, Any]], destination_path: str) -> Optional[str]:
        """Upload data as JSONL to storage"""
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                for item in data_list:
                    temp_file.write(json.dumps(item) + "\n")
                temp_path = temp_file.name

            return await self.storage_service.upload_file(bucket_name=bucket_name, file_path=temp_path, destination_path=destination_path, content_type="application/x-jsonlines")

        finally:
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.remove(temp_path)

    async def upload_text(self, bucket_name: str, text_content: str, destination_path: str) -> Optional[str]:
        """
        Upload text content to a GCS bucket.

        Args:
            bucket_name: Name of the GCS bucket
            text_content: Text content to upload
            destination_path: Destination path in the bucket
        """
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                temp_file.write(text_content)
                temp_file.flush()
                temp_path = temp_file.name

                return await self.storage_service.upload_file(bucket_name=bucket_name, file_path=temp_path, destination_path=destination_path, content_type="text/plain")
        finally:
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
