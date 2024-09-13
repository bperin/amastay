from scraper import Scraper
import logging
import uuid

# Configure logging for the test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_scraper():
    """
    Function to test the Scraper class.
    """
    try:
        # Example Property ID from Supabase (use a real property UUID from your database)
        property_id = str(uuid.uuid4())  # Use a new UUID for each test

        # URL to scrape (Ensure that scraping the URL won't be blocked by rate-limits)
        url_to_scrape = "https://www.airbnb.com/rooms/1035914537235834436?category_tag=Tag%3A670&enable_m3_private_room=true&photo_id=1791475063&search_mode=regular_search&check_in=2024-09-20&check_out=2024-09-21&source_impression_id=p3_1726102320_P3c2GGVcc1OkEHBa&previous_page_section_name=1000&federated_search_id=8cb2009c-bb4e-461b-ae44-26967cdc1d55"

        # Instantiate the scraper
        scraper = Scraper(url_to_scrape)

        # Scrape the content
        logging.info("Starting the scraping process.")
        document = scraper.scrape()

        if document:
            logging.info(f"Scraped document length: {len(document)} characters")

            # Check document content more deeply
            if len(document) > 200:
                logging.info("Document looks valid based on length.")

            # Ensure some basic structure or keywords exist in the document
            if "URL: https://www.airbnb.com/rooms" in document:
                logging.info("Document contains the expected URL metadata.")
            else:
                logging.warning("Document does not contain expected URL metadata.")
                
            # Proceed to upload the document to Supabase
            logging.info("Uploading document to Supabase.")
            response = scraper.upload_document_to_supabase(property_id, document)

            # Verify the response from Supabase
            if response:
                logging.info(f"Upload response: {response}")
                if response.status_code == 201:
                    logging.info("Document successfully uploaded.")
                else:
                    logging.error(f"Failed to upload document. Supabase responded with: {response.json()}")
            else:
                logging.error("Upload to Supabase failed with no response.")
        else:
            logging.error("Scraping failed, no document returned.")

    except Exception as e:
        logging.error(f"Test failed with error: {str(e)}")

if __name__ == "__main__":
    # Run the test
    test_scraper()
