import logging
import os
import tempfile
import aiohttp
from typing import Optional
from services.storage_service import StorageService


class PhotoService:
    """Service for handling photo operations"""

    def __init__(self):
        self.storage_service = StorageService()

    async def upload_from_url(self, bucket_name: str, photo_url: str, destination_path: str, content_type: str = "image/jpeg") -> Optional[str]:
        """Download photo from URL and upload to storage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(photo_url) as response:
                    if response.status != 200:
                        logging.error(f"Failed to download photo from {photo_url}")
                        return None

                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(await response.read())
                        temp_path = temp_file.name

                    try:
                        return await self.storage_service.upload_file(bucket_name=bucket_name, file_path=temp_path, destination_path=destination_path, content_type=content_type)
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

        except Exception as e:
            logging.error(f"Error uploading photo from URL {photo_url}: {e}")
            raise
