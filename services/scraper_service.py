from .scraper import Scraper  # Import the Scraper class


class ScraperService:
    """Service for scraping property data"""

    def __init__(self):
        if not SCRAPER_BASE_URL or not SCRAPER_API_KEY:
            raise ValueError("Scraper configuration is missing. Check environment variables.")
        self.storage_service = StorageService()
        self.scraper = Scraper(SCRAPER_BASE_URL, SCRAPER_API_KEY)  # Initialize the Scraper

    async def _scrape_property_data(self, property_url: str) -> dict:
        """Fetch and process property data from scraper service"""
        try:
            data = await self.scraper.scrape_property_data(property_url)  # Use the Scraper class
            return data
        except Exception as e:
            logging.error(f"Error scraping property data: {str(e)}")
            raise
