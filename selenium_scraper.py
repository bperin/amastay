from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging

# Configure logging (this is optional and can be adjusted based on your needs)
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO or lower to reduce output
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("selenium_scraper.log"),  # Log to file
        logging.StreamHandler(),  # Also log to console
    ],
)


def configure_selenium():
    """Configure Selenium for headless mode and reduced logging."""
    # Chrome options to run headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Prevents Chrome from crashing in some environments
    chrome_options.add_argument("--window-size=1920,1080")  # Optional: set window size

    # Suppress logging by setting log-level
    chrome_options.add_argument("--log-level=3")  # Suppress most logs (INFO level)

    # Create a service object and suppress driver logs
    service = Service(log_path="/dev/null")  # Discard logs (Linux/Mac). On Windows, use 'NUL' instead of '/dev/null'

    # Initialize the Chrome WebDriver with options and service
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scrape_page(url):
    """Example of scraping a page using Selenium."""
    driver = configure_selenium()
    try:
        driver.get(url)  # Navigate to the page
        content = driver.page_source  # Get the page source (HTML content)
        logging.info(f"Scraped {len(content)} characters from {url}")
    finally:
        driver.quit()  # Ensure that the browser closes properly


if __name__ == "__main__":
    # Example usage
    url = "https://www.airbnb.com"
    scrape_page(url)
