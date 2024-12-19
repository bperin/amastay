import logging
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver  # Import Selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # Automatically manage ChromeDriver

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)


class Scraper:
    def __init__(self):
        # Set up Selenium WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def filter_content(self, soup):
        """Filter out unwanted content and clean the text."""
        logging.debug("Filtering content from the soup object.")

        # Remove non-content tags
        for tag in soup.select("script, style, header, footer, nav, aside, noscript, meta, link, button, svg, iframe, form"):
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

    def scrape_url(self, url):
        """Scrape content from a single URL using Selenium."""
        logging.info(f"Starting scrape for URL: {url}")

        try:
            self.driver.get(url)  # Use Selenium to get the page
            soup = BeautifulSoup(self.driver.page_source, "html.parser")  # Get the rendered HTML
            filtered_text = self.filter_content(soup)

            airbnb_match = re.search(r"https://www\.airbnb\.com/rooms/(\d+)", url)

            if airbnb_match:
                room_id = airbnb_match.group(1)
                urls = [url, f"https://www.airbnb.com/rooms/{room_id}/reviews", f"https://www.airbnb.com/rooms/{room_id}/amenities"]

                combined_text = []
                for scrape_url in urls:
                    logging.info(f"Scraping URL: {scrape_url}")
                    try:
                        self.driver.get(scrape_url)  # Use Selenium to get the page
                        soup = BeautifulSoup(self.driver.page_source, "html.parser")  # Get the rendered HTML
                        filtered_text = self.filter_content(soup)

                        if filtered_text:
                            if "/reviews" in scrape_url:
                                section_name = "REVIEWS"
                            elif "/amenities" in scrape_url:
                                section_name = "AMENITIES"
                            else:
                                section_name = "MAIN LISTING"
                            combined_text.append(f"\n=== {section_name} ===\n{filtered_text}")
                    except Exception as e:
                        logging.error(f"Error scraping {scrape_url}: {e}", exc_info=True)

                final_text = "\n".join(combined_text)
                logging.info(f"Filtered document length: {len(final_text)} characters")
                return final_text if final_text else "No content found"

            else:
                logging.info(f"Filtered document length: {len(filtered_text)} characters")
                return filtered_text if filtered_text else "No content found"

        except Exception as e:
            logging.error(f"Error during scraping: {e}", exc_info=True)
            return None

    def close(self):
        """Close the Selenium WebDriver."""
        self.driver.quit()

    async def scrape(self, url):
        """Start scraping process for a single URL."""
        result = self.scrape_url(url)
        return result
