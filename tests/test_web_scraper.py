import unittest
import logging
import uuid
from scraper import Scraper
from unittest.mock import patch, MagicMock
import requests  # Import requests to validate connection errors

# Configure logging for the test
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TestScraper(unittest.TestCase):

    @patch('scraper.Scraper.upload_document_to_supabase')  # Mock the upload function
    @patch('scraper.Scraper.save_document_to_database')  # Mock the database save function
    def test_scraper(self, mock_db_save, mock_upload):
        """
        Function to test the Scraper class with a focus on saving the document and
        making sure it is stored regardless of whether the database entry succeeds.
        """
        # Set up the mock response for file upload to simulate a successful upload
        mock_upload_response = MagicMock()
        mock_upload_response.status_code = 201  # Simulate a successful HTTP 201 Created response
        mock_upload.return_value = mock_upload_response  # Mock the return value of the upload function

        # Set up the mock response for database save to simulate a failure
        mock_db_save.side_effect = Exception("Database save failed")  # Simulate a database failure

        try:
            # Example Property ID from Supabase (use a fake UUID for testing)
            property_id = str(uuid.uuid4())  # Use a new UUID for each test

            # URL to scrape (Ensure that scraping the URL won't be blocked by rate-limits)
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
                
            # Test: Uploading the document to Supabase (regardless of database entry)
            logging.info("Uploading document to Supabase.")
            response = scraper.upload_document_to_supabase(property_id, document)

            # Validate the Supabase file upload response
            self.assertIsNotNone(response, "Upload to Supabase failed: No response from Supabase.")
            self.assertEqual(response.status_code, 201, f"Supabase upload failed with status code {response.status_code}")

            # Test: Saving the document to the database
            logging.info("Attempting to save document metadata to the database.")
            try:
                scraper.save_document_to_database(property_id, document)
            except Exception as db_error:
                logging.warning(f"Database save failed: {db_error}")
                # The test should not fail if the DB save fails, only log it

        except requests.ConnectionError as ce:
            logging.error(f"Connection error during scraping or upload: {ce}")
            self.fail(f"Connection error occurred: {ce}")
        except Exception as e:
            logging.error(f"Test failed with error: {str(e)}")
            self.fail(f"Test failed with unexpected error: {str(e)}")

if __name__ == "__main__":
    unittest.main()

