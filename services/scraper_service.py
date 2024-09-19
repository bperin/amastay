import logging
import uuid
from scraper import Scraper
from supabase_utils import supabase_client

class ScraperService:

    @staticmethod
    def scrape_and_save(url: str, property_id: str) -> dict:
        """
        Scrapes the content from the URL, uploads it to Supabase storage, and saves the document metadata in the database.
        """
        # Initialize the scraper and scrape the content
        scraper = Scraper(url)
        scraped_content = scraper.scrape()

        if not scraped_content:
            raise Exception("Failed to scrape the data")

        # Upload scraped content to Supabase storage
        storage_response = scraper.upload_document_to_supabase(property_id, scraped_content)
        if not storage_response:
            raise Exception("Failed to upload the scraped document")

        # Store the scraped document metadata in the database
        db_response = scraper.save_document_to_database(property_id, scraped_content)
        if not db_response:
            raise Exception("Failed to save the document to the database")

        # Return a success message and the responses
        return {
            "message": "Scraping and file upload successful",
            "property_id": property_id,
            "storage_response": storage_response,
            "db_response": db_response.data
        }
