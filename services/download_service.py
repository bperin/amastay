import aiohttp
import logging
from typing import Optional, Tuple, Union
import io
import asyncio


class DownloadService:
    """Service for downloading files from URLs"""

    @staticmethod
    async def download_from_url(url: str) -> Optional[Tuple[Union[bytes, io.BytesIO], str]]:
        """
        Download content from URL
        Returns tuple of (content, content_type) or None if failed
        """
        try:
            logging.info(f"Starting download from URL: {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logging.error(f"Failed to download from {url}. Status: {response.status}")
                        return None

                    content_type = response.headers.get("content-type", "application/octet-stream")
                    content = await response.read()
                    content_length = len(content)
                    logging.info(f"Successfully downloaded {content_length} bytes from {url}")

                    return content, content_type

        except Exception as e:
            logging.error(f"Error downloading from {url}: {e}")
            return None

    @staticmethod
    async def download_images(urls: list[str]) -> list[Tuple[bytes, str]]:
        """
        Download multiple images in parallel
        Returns list of (content, content_type) tuples
        """
        logging.info(f"Starting batch download of {len(urls)} images")
        results = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in urls:
                tasks.append(DownloadService.download_from_url(url))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for url, response in zip(urls, responses):
                if isinstance(response, Exception):
                    logging.error(f"Failed to download {url}: {response}")
                    continue
                if response:
                    results.append(response)

        logging.info(f"Successfully downloaded {len(results)} out of {len(urls)} images")
        return results
