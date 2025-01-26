import logging
import os
import aiohttp
from models.property_model import Property
from supabase_utils import supabase_client
import asyncio
from dotenv import load_dotenv
from services.llama_service_vertex import LlamaService

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

    @staticmethod
    async def scrape_property_background(property: Property) -> None:
        """Background task for property scraping"""
        try:
            if not property.property_url:
                logging.info(f"No 'property_url' provided for property {property.id}")
                return

            # Set initial progress
            supabase_client.table("properties").update({"metadata_progress": 1}).eq("id", property.id).execute()

            # Fetch property data from external scraper
            data = await ScraperService._scrape_property_data(property.property_url)
            logging.info(f"Received scraper response for property {property.id}")

            # Create metadata entry
            metadata = {"property_id": property.id, "data": data, "scraped": True}
            response = supabase_client.table("property_metadata").insert(metadata).execute()
            if not response.data:
                raise ValueError(f"Failed to insert metadata: {response.error}")

            # Update property metadata
            metadata_id = response.data[0]["id"]
            supabase_client.table("properties").update({"metadata_id": metadata_id, "metadata_progress": 2}).eq("id", property.id).execute()

            logging.info(f"Scraping completed for property {property.id}")

        except Exception as e:
            logging.error(f"Failed to scrape property {property.id}: {e}")
            # Update property to show error state
            supabase_client.table("properties").update({"metadata_progress": -1}).eq("id", property.id).execute()
            raise
