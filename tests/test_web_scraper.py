import logging
import unittest
import uuid

from scraper import Scraper

class TestScraper(unittest.TestCase):
    def test_scraper(self):
        try:
            # Example Property ID from Supabase (use a fake UUID for testing)
            property_id = str(uuid.uuid4())  # Use a new UUID for each test

            # URL to scrape
            url_to_scrape = "https://www.airbnb.com/rooms/1035914537235834436"

            # Instantiate the scraper
            scraper = Scraper(url_to_scrape)

            # Scrape the data
            logging.info(f"Starting the scraping process for {url_to_scrape}.")
            scraped_data = scraper.scrape()

            # Ensure data is scraped
            self.assertIsNotNone(scraped_data, "Scraping failed. No data returned.")
            logging.info(f"Scraped data length: {len(scraped_data)}")

            # Save the scraped data to Supabase
            logging.info("Uploading scraped data to Supabase.")
            filename = scraper.save_scraped_data(property_id, scraped_data)

            # Check for issues with filename or response
            if filename is None:
                logging.error("Upload failed: Filename returned as None.")
                raise ValueError("Filename is None after upload. Check upload process.")

            # Ensure the file was uploaded
            self.assertIsNotNone(filename, "Upload to Supabase failed: No filename returned.")
            logging.info(f"File uploaded successfully: {filename}")

        except FileNotFoundError as fnfe:
            logging.error(f"File not found error: {fnfe}")
            self.fail(f"FileNotFoundError occurred: {fnfe}")

        except IOError as ioe:
            logging.error(f"I/O error while processing the file: {ioe}")
            self.fail(f"IOError occurred: {ioe}")

        except Exception as e:
            logging.error(f"Test failed with error: {str(e)}")
            self.fail(f"Test failed with unexpected error: {str(e)}")

if __name__ == "__main__":
    unittest.main()
