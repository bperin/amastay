import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import logging
from urllib.parse import urlparse  # To parse the domain from URL
from utils import supabase  # Import Supabase client from utils.py

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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
        Tries multiple scraping methods (different headers, User-Agents).
        Stops once one method succeeds and returns the plain text content with metadata.
        """
        headers_list = self.get_headers_list()

        logging.info(f"Starting scrape for URL: {self.url}")

        for i, headers in enumerate(headers_list):
            try:
                logging.info(f"Trying method {i+1} with headers: {headers['User-Agent']}")
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

            # Random delay to avoid detection
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
            response = requests.get(self.url, headers=headers)
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def create_document(self, response):
        """
        Parses the webpage content, extracts plain text, and formats it into a document with metadata.
        """
        soup = BeautifulSoup(response.content, 'html.parser')
        plain_text = soup.get_text(separator="\n", strip=True)  # Get all text with line breaks

        # Create a plain text document with metadata
        document = f"URL: {self.url}\nScraped on: {datetime.now()}\n\n{plain_text}"
        logging.info(f"Created document with {len(document)} characters.")
        return document

    def generate_filename(self, property_id):
        """
        Generates a unique filename based on the property ID, URL, and timestamp.
        """
        parsed_url = urlparse(self.url)
        domain = parsed_url.netloc.replace('.', '_')  # Replace dots with underscores in domain
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format the current timestamp

        # Construct a unique filename: property_id + domain + timestamp
        filename = f"{property_id}_{domain}_{timestamp}.txt"
        return filename

    def upload_document_to_supabase(self, property_id, document):
        """
        Uploads the scraped document to the Supabase bucket 'properties'.
        """
        data = {
            'id': str(uuid.uuid4()),  # New UUID for the document
            'foreign_id': property_id,  # Property UUID (foreign key)
            'url': self.url,
            'scraped_data': document,  # Store the scraped data in the database
            'timestamp': str(datetime.now())
        }

        try:
            # Generate a unique filename for each document
            filename = self.generate_filename(property_id)

            # Upload document to the 'properties' bucket in Supabase
            response = supabase.storage.from_('properties').upload(filename, document)

            if response:
                logging.info(f"Document uploaded successfully to Supabase with filename: {filename}. Property ID: {property_id}")
            else:
                logging.error(f"Failed to upload document to Supabase. Response: {response}")

        except Exception as e:
            logging.error(f"Failed to upload document to Supabase: {str(e)}")

        # Insert metadata into the database table
        try:
            db_response = supabase.from_('scraped_documents').insert(data).execute()
            if db_response.status_code == 201:
                logging.info(f"Document metadata inserted successfully. Property ID: {property_id}")
            else:
                logging.error(f"Failed to insert document metadata: {db_response.status_code}. Error: {db_response.json()}")
        except Exception as e:
            logging.error(f"Failed to insert document metadata into Supabase: {str(e)}")

        return response

    def get_headers_list(self):
        """
        Returns a list of different headers (User-Agents) to try.
        """
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
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': '',
            }
        ]
