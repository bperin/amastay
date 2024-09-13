import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import logging
import os
import tempfile
from urllib.parse import urlparse
from utils import supabase  # Import Supabase client from utils.py

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

class Scraper:
    def __init__(self, url):
        self.url = url

    def scrape(self):
        """
        Scrape the webpage content from the URL.
        """
        headers_list = self.get_headers_list()

        logging.info(f"Starting scrape for URL: {self.url}")

        for i, headers in enumerate(headers_list):
            try:
                logging.debug(f"Trying method {i+1} with headers: {headers['User-Agent']}")
                response = self.fetch_data(headers)

                if response and response.status_code == 200:
                    logging.info(f"Success on method {i+1}! Status code: {response.status_code}")
                    document = self.create_document(response)
                    logging.debug(f"Scraped content (first 200 characters): {document[:200]}...")
                    return document
                else:
                    logging.warning(f"Method {i+1} failed. Status code: {response.status_code if response else 'No response'}")
            except Exception as e:
                logging.error(f"Error on method {i+1}: {str(e)}")

            sleep_time = random.uniform(2, 5)
            logging.info(f"Waiting for {sleep_time:.2f} seconds before next attempt...\n")
            time.sleep(sleep_time)

        logging.error("All methods failed.")
        return None

    def fetch_data(self, headers):
        """
        Fetches the webpage using the provided headers.
        """
        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def create_document(self, response):
        """
        Parses the webpage content, extracts plain text, and formats it into a document with metadata.
        """
        soup = BeautifulSoup(response.content, 'html.parser')
        plain_text = soup.get_text(separator="\n", strip=True)

        # Create a plain text document with metadata
        document = f"URL: {self.url}\nScraped on: {datetime.now()}\n\n{plain_text}"
        logging.info(f"Created document with {len(document)} characters.")
        return document

    def upload_document_to_supabase(self, property_id, document):
        """
        Uploads the scraped document to Supabase storage.
        """
        filename = f"{property_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        temp_file_path = None  # Ensure temp_file_path is defined

        try:
            # Save the scraped content to a temporary file before uploading
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(document.encode())  # Write document content to file
                temp_file.seek(0)  # Move the cursor back to the beginning of the file
                temp_file_path = temp_file.name

            # Upload the temporary file to Supabase storage
            response = supabase.storage.from_('properties').upload(filename, temp_file_path)

            # Check if the upload was successful
            if response:
                logging.info(f"Document uploaded successfully as {filename}")
            else:
                logging.error(f"Failed to upload document: {response}")
            return response

        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            return None

        finally:
            # Cleanup: Remove the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logging.info("Temporary file deleted.")

    def save_document_to_database(self, property_id, file_url):
        """
        Save metadata related to the scraped document to the database.
        The document is stored as a file in Supabase, and this method
        stores a reference to the file.
        
        :param property_id: UUID of the property
        :param file_url: URL or pointer to the file in Supabase storage
        """
        data = {
            'property_id': property_id,
            'url': self.url,
            'file_url': file_url,  # Pointer to the file in storage (instead of the full document)
            'timestamp': str(datetime.now())  # Current timestamp
        }

        logging.info("Inserting document metadata into the database.")
        try:
            # Insert the metadata (including the file URL) into the database
            response = supabase.from_('scraped_documents').insert(data).execute()

            # Check if the insert was successful
            if response.status_code == 201:
                logging.info(f"Document metadata inserted successfully for Property ID: {property_id}")
            else:
                logging.error(f"Failed to insert document metadata: {response.status_code}")
            return response
        except Exception as e:
            logging.error(f"Error inserting document metadata: {e}")
            return None


    def get_headers_list(self):
        """
        Returns a list of different headers (User-Agents) to try for the requests.
        """
        logging.debug("Generating list of headers for scraping.")
        return [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.bing.com/',
            },
            {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
            },
            {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 3 XL Build/PQ2A.190405.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.airbnb.com/',
            },
        ]

