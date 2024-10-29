import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from supabase_utils import supabase_client
import tempfile
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
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
        options.add_argument("--enable-javascript")

        # Initialize the Chrome driver (Make sure chromedriver is installed)
        self.driver = webdriver.Chrome(options=options)

    def filter_content(self, soup):
        """Filter out unwanted content such as headers, footers, and calendar elements."""
        # Remove irrelevant tags
        for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
            tag.decompose()

        # Remove calendar elements based on their known class or ID (modify this selector as needed)
        for calendar_tag in soup.find_all(class_="calendar"):
            calendar_tag.decompose()

        # Remove any specific elements with text patterns like 'Add your travel dates'
        for tag in soup.find_all(string=lambda text: "Add your travel dates" in text or "Su Mo Tu We Th Fr Sa" in text):
            parent_tag = tag.find_parent()
            if parent_tag:
                parent_tag.decompose()

        # Extract meaningful text
        text = soup.get_text(separator="\n", strip=True)

        # Post-process the text to remove excessive newlines and white spaces
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        return clean_text

    def scrape(self):
        """Scrape content from the page using Selenium to render it."""
        self.init_selenium()
        logging.info(f"Starting Selenium scrape for URL: {self.url}")

        try:
            # Check if URL is an Airbnb listing
            airbnb_match = re.match(r'https://www\.airbnb\.com/rooms/(\d+)/?$', self.url)
            
            if airbnb_match:
                room_id = airbnb_match.group(1)
                urls = [
                    self.url,  # Main listing
                    f"https://www.airbnb.com/rooms/{room_id}/reviews",  # Reviews
                    f"https://www.airbnb.com/rooms/{room_id}/amenities"  # Amenities
                ]
                combined_text = []
                
                for url in urls:
                    self.driver.get(url)
                    time.sleep(5)  # Adjust sleep time to allow the page to load fully
                    
                    page_source = self.driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")
                    filtered_text = self.filter_content(soup)
                    
                    if filtered_text:
                        section_name = "MAIN LISTING" if url == self.url else "REVIEWS" if "/reviews" in url else "AMENITIES"
                        combined_text.append(f"\n=== {section_name} ===\n{filtered_text}")
                
                final_text = "\n".join(combined_text)
                logging.info(f"Filtered document length: {len(final_text)} characters")
                return final_text if final_text else "No content found"
            
            else:
                # Handle non-Airbnb URLs as before
                self.driver.get(self.url)
                time.sleep(5)
                
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
                filtered_text = self.filter_content(soup)
                
                logging.info(f"Filtered document length: {len(filtered_text)} characters")
                return filtered_text if filtered_text else "No content found"
                
        except Exception as e:
            logging.error(f"Error during scraping: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
