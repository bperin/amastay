import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client
import os

class Scraper:
    def __init__(self, url, property_id):
        self.url = url
        self.property_id = property_id  # Foreign key from the properties table

        # Initialize Supabase client (assumes environment variables are set)
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase = create_client(self.supabase_url, self.supabase_key)

    def scrape(self):
        """
        Tries multiple scraping methods (different headers, User-Agents).
        Stops once one method succeeds and returns the plain text content with metadata.
        """
        headers_list = self.get_headers_list()
        
        for i, headers in enumerate(headers_list):
            try:
                print(f"Trying method {i+1} with headers: {headers['User-Agent']}")
                response = self.fetch_data(headers)

                if response and response.status_code == 200:
                    print(f"Success on method {i+1}! Status code: {response.status_code}")
                    document = self.create_document(response)
                    self.upload_document_to_supabase(document)
                    return document
                else:
                    print(f"Method {i+1} failed. Status code: {response.status_code if response else 'No response'}")
            
            except Exception as e:
                print(f"Error on method {i+1}: {str(e)}")

            # Random delay to avoid detection
            sleep_time = random.uniform(2, 5)
            print(f"Waiting for {sleep_time:.2f} seconds before next attempt...\n")
            time.sleep(sleep_time)

        print("All methods failed.")
        return None

    def fetch_data(self, headers):
        """
        Fetches the webpage using the provided headers.
        """
        response = requests.get(self.url, headers=headers)
        return response

    def create_document(self, response):
        """
        Parses the webpage content, extracts plain text, and formats it into a document with metadata.
        """
        soup = BeautifulSoup(response.content, 'html.parser')
        plain_text = soup.get_text(separator="\n", strip=True)  # Get all text with line breaks

        # Create a plain text document with metadata (property ID, URL, and timestamp)
        document = f"Property ID: {self.property_id}\nURL: {self.url}\nScraped on: {datetime.now()}\n\n{plain_text}"
        return document

    def upload_document_to_supabase(self, document):
        """
        Uploads the scraped document to the Supabase table.
        """
        data = {
            'property_id': self.property_id,
            'url': self.url,
            'scraped_data': document,
            'timestamp': str(datetime.now())
        }

        response = self.supabase.from_('scraped_documents').insert(data).execute()
        if response.status_code == 201:
            print("Document uploaded successfully to Supabase.")
        else:
            print(f"Failed to upload document: {response.status_code}")

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
