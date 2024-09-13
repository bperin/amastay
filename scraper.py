import logging
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from utils import supabase  # Import Supabase client from utils.py
import tempfile
import os

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
        self.driver = None
        self.headers_list = self.get_headers_list()
        self.current_header_index = 0

    def init_selenium(self):
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        headers = self.get_next_header()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument(f"user-agent={headers['User-Agent']}")

        self.driver = webdriver.Chrome(options=options)

    def scrape_search_results(self):
        self.init_selenium()
        logging.info(f"Starting Selenium scrape for Search Results")
        try:
            self.driver.get(self.url)
            time.sleep(5)  # Adjust this timeout as needed

            # Simulate scrolling behavior
            for _ in range(4):
                self.driver.execute_script("window.scrollBy(0, 1000);")
                sleep_time = random.uniform(2, 3)
                logging.info(f"Simulating scroll and sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

            # Extract data from the loaded page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            search_results = []
            for result in soup.find_all('div', class_='search-result'):
                title = result.find('h2').text.strip()
                description = result.find('p').text.strip()
                search_results.append({'title': title, 'description': description})

            logging.info(f"Extracted {len(search_results)} search results")
            return search_results if search_results else "No search results found."

        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return None

    def scrape(self):
        self.init_selenium()
        logging.info(f"Starting Selenium scrape for URL: {self.url}")
        try:
            data = self.scrape_search_results()  # Use the new method
            if data is not None:
                return data
            else:
                raise Exception("Failed to extract search results")
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return None

    def save_scraped_data(self, property_id, scraped_data):
        """
        Saves the scraped data to a file and uploads it to Supabase.
        Converts lists into strings if needed.
        """
        if isinstance(scraped_data, list):
            scraped_data = '\n'.join([f"Title: {item['title']}\nDescription: {item['description']}" for item in scraped_data])

        # Create a temporary file and write the scraped data to it
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(scraped_data.encode('utf-8'))  # Write data as bytes
                temp_file_path = temp_file.name

            # Generate filename
            filename = f"{property_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            response = supabase.storage.from_('properties').upload(filename, temp_file_path)

            if response:
                logging.info(f"Document uploaded successfully as {filename}")
                return filename
            else:
                logging.error(f"Failed to upload document: {response}")
                return None

        except Exception as e:
            logging.error(f"Error saving scraped data to Supabase: {e}")
            return None

        finally:
            # Cleanup temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logging.info(f"Temporary file '{temp_file_path}' deleted.")

    def get_next_header(self):
        headers = self.headers_list[self.current_header_index]
        self.current_header_index = (self.current_header_index + 1) % len(self.headers_list)
        return headers

    def get_headers_list(self):
        return [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3',
                'Accept-Language': 'en-US,en;q=0.9'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            },
            {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
                'Accept-Language': 'en-US,en;q=0.9'
            }
        ]
