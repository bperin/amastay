import logging
import time
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
        logging.info(f"Initialized Scraper with URL: {self.url}")

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
        self.driver = webdriver.Chrome(options=options)
        logging.info("Selenium WebDriver initialized.")

    def filter_content(self, soup):
        """Filter out unwanted content and clean the text."""
        logging.debug("Filtering content from the soup object.")
        # Remove non-content tags
        for tag in soup(["script", "style", "header", "footer", "nav", "aside", "noscript", "meta", "link", "button", "svg", "iframe", "form"]):
            tag.decompose()

        # Remove elements known to contain irrelevant content
        for cal in soup.select(".calendar"):
            cal.decompose()

        # Remove hidden elements
        for hidden in soup.select("[aria-hidden='true'], [style*='display:none']"):
            hidden.decompose()

        # Extract and clean text
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Define sets of unwanted lines
        day_abbrevs = {"Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"}
        months = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"}

        filtered_lines = []
        for line in lines:
            if line in day_abbrevs or line in months or line.isdigit():
                continue
            filtered_lines.append(line)

        clean_text = "\n".join(filtered_lines)
        logging.debug("Content filtering complete.")
        return clean_text

    async def scrape(self):
        """Scrape content from the page using Selenium to render it."""
        logging.info(f"Starting scrape for URL: {self.url}")
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, self._scrape_sync)

    def _scrape_sync(self):
        """Synchronous scraping implementation to run in thread pool."""
        self.init_selenium()
        logging.info(f"Starting Selenium scrape for URL: {self.url}")

        try:
            airbnb_match = re.search(r"https://www\.airbnb\.com/rooms/(\d+)", self.url)

            if airbnb_match:
                room_id = airbnb_match.group(1)
                urls = [self.url, f"https://www.airbnb.com/rooms/{room_id}/reviews", f"https://www.airbnb.com/rooms/{room_id}/amenities"]

                combined_text = []
                for url in urls:
                    logging.info(f"Scraping URL: {url}")
                    self.driver.get(url)
                    time.sleep(2)

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
                self.driver.get(self.url)
                time.sleep(2)

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
                logging.info("Selenium WebDriver closed.")
