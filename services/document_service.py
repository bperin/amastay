import json
import logging
import os
import tempfile
from typing import Optional, Dict, Any
from .storage_service import StorageService
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
        """Upload text content to GCS"""
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
                temp_file.write(text_content)
                temp_file.flush()

                # If uploading to property text bucket, set update_search_index to True
                update_search_index = bucket_name == "amastay_property_data_text"

                return await self.storage_service.upload_file(bucket_name=bucket_name, file_path=temp_file.name, destination_path=destination_path, content_type="text/plain", update_search_index=update_search_index)
        except Exception as e:
            logging.error(f"Error uploading text content: {e}")
            raise
        finally:
            if "temp_file" in locals():
                os.unlink(temp_file.name)
