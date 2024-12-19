import logging
import time
import re
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc  # Import undetected-chromedriver
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)


class Scraper:
    @staticmethod
    def init_selenium():
        """Initialize and return the Selenium WebDriver with options."""
        try:
            options = uc.ChromeOptions()
            options.headless = True  # Enable headless mode

            # Essential arguments for running Chrome in Docker
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-extensions")
            options.add_argument("--enable-javascript")
            options.add_argument("--window-size=1920x1080")  # Set window size for headless mode
            options.add_argument("--disable-gpu")  # Disable GPU acceleration
            options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
            options.add_argument("--disable-blink-features=AutomationControlled")  # Bypass detection

            # Specify the path to the Chrome binary inside Docker
            # options.binary_location = "/usr/bin/google-chrome"

            # Initialize the Chrome driver
            driver = uc.Chrome(options=options)
            logging.info("Selenium WebDriver initialized with undetected-chromedriver.")
            return driver

        except Exception as e:
            logging.error(f"Failed to initialize Selenium WebDriver: {e}", exc_info=True)
            raise

    @staticmethod
    def filter_content(soup):
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

    @staticmethod
    async def scrape(url):
        """Scrape content from the page using Selenium to render it."""
        logging.info(f"Starting scrape for URL: {url}")
        driver = Scraper.init_selenium()  # Initialize the driver

        try:
            airbnb_match = re.search(r"https://www\.airbnb\.com/rooms/(\d+)", url)

            if airbnb_match:
                room_id = airbnb_match.group(1)
                urls = [url, f"https://www.airbnb.com/rooms/{room_id}/reviews", f"https://www.airbnb.com/rooms/{room_id}/amenities"]

                combined_text = []
                for scrape_url in urls:
                    logging.info(f"Scraping URL: {scrape_url}")
                    driver.get(scrape_url)
                    time.sleep(2)  # Consider replacing with explicit waits for better reliability

                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, "html.parser")
                    filtered_text = Scraper.filter_content(soup)

                    if filtered_text:
                        if "/reviews" in scrape_url:
                            section_name = "REVIEWS"
                        elif "/amenities" in scrape_url:
                            section_name = "AMENITIES"
                        else:
                            section_name = "MAIN LISTING"
                        combined_text.append(f"\n=== {section_name} ===\n{filtered_text}")

                final_text = "\n".join(combined_text)
                logging.info(f"Filtered document length: {len(final_text)} characters")
                return final_text if final_text else "No content found"

            else:
                driver.get(url)
                time.sleep(2)  # Consider replacing with explicit waits for better reliability

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
                filtered_text = Scraper.filter_content(soup)

                logging.info(f"Filtered document length: {len(filtered_text)} characters")
                return filtered_text if filtered_text else "No content found"

        except Exception as e:
            logging.error(f"Error during scraping: {e}", exc_info=True)
            return None
        finally:
            if driver:
                driver.quit()
                logging.info("Selenium WebDriver closed.")
