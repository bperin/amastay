import unittest
import logging
import uuid
from scraper import Scraper
import requests

# Configure logging for the test
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestScraper(unittest.TestCase):

    def test_scraper(self):
        """
        Function to test the Scraper class with actual uploading and saving.
        """
        try:
            # Example Property ID from Supabase (use a real or test UUID for testing)
            property_id = str(uuid.uuid4())  # Generate a new UUID for each test

            # URL to scrape
            url_to_scrape = "https://www.airbnb.com/rooms/1035914537235834436"

            # Instantiate the scraper
            scraper = Scraper(url_to_scrape)

            # Start of test: Scraping
            logging.info(f"Starting the scraping process for {url_to_scrape}.")
            document = scraper.scrape()

            # Check if the document was successfully scraped
            self.assertIsNotNone(document, "Scraping failed. No document returned.")

            # Log document size
            logging.info(f"Scraped document length: {len(document)} characters")

            # Check document content more deeply
            self.assertGreater(len(document), 200, "Document is too short, scraping may have failed.")
            self.assertIn("URL: https://www.airbnb.com/rooms", document, "Document does not contain expected URL metadata.")
                
            # Start of test: Uploading to Supabase
            logging.info("Uploading document to Supabase.")

            # Attempt to upload the document to Supabase
            document_url = scraper.upload_document_to_supabase(property_id, document)
            self.assertIsNotNone(document_url, "Upload to Supabase failed: No URL returned.")

            # Test saving the document metadata in the database
            db_response = scraper.save_document_to_database(property_id, document_url)
            self.assertEqual(db_response.status_code, 201, "Failed to save document metadata to the database")

            logging.info(f"Test completed successfully for property ID: {property_id}.")

        except requests.ConnectionError as ce:
            logging.error(f"Connection error during scraping or upload: {ce}")
            self.fail(f"Connection error occurred: {ce}")
        except Exception as e:
            logging.error(f"Test failed with error: {str(e)}")
            self.fail(f"Test failed with unexpected error: {str(e)}")


if __name__ == "__main__":
    unittest.main()
