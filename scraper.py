import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils import supabase
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

    def init_selenium(self):
        """Initialize the Selenium WebDriver with options."""
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")

        # Initialize the Chrome driver (Make sure chromedriver is installed)
        self.driver = webdriver.Chrome(options=options)

    def filter_content(self, soup):
        """Filter out unwanted content such as headers, footers, and navigation elements."""
        # Remove irrelevant tags
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()

        # Extract meaningful text
        text = soup.get_text(separator='\n', strip=True)

        # Post-process the text to remove excessive newlines and white spaces
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = '\n'.join(lines)
        return clean_text

    def scrape(self):
        """Scrape content from the page using Selenium to render it."""
        self.init_selenium()
        logging.info(f"Starting Selenium scrape for URL: {self.url}")

        try:
            # Load the page and let it render
            self.driver.get(self.url)
            time.sleep(5)  # Adjust sleep time to allow the page to load fully

            # Get the page source and parse it with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Filter the content to remove unnecessary parts
            filtered_text = self.filter_content(soup)
            logging.info(f"Filtered document length: {len(filtered_text)} characters")

            return filtered_text if filtered_text else "No content found"
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()

    def save_scraped_data(self, property_id, scraped_data):
        """Save scraped data as a text file to Supabase."""
        filename = f"{property_id}_{int(time.time())}.txt"
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(scraped_data.encode('utf-8'))
                temp_file_path = temp_file.name

            # Upload to Supabase
            response = supabase.storage.from_('properties').upload(filename, temp_file_path)

            if response:
                logging.info(f"Document uploaded successfully as {filename}")
                os.remove(temp_file_path)  # Clean up temp file
                return filename
            else:
                logging.error(f"Failed to upload document to Supabase.")
                return None
        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            return None
