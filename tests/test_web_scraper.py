from scraper import Scraper

# Example usage of the scraper
if __name__ == "__main__":
    # Example URL of the property
    url = "https://www.airbnb.com/rooms/677814898295718643"

    # Property ID from the properties table (UUID)
    property_id = "123e4567-e89b-12d3-a456-426614174000"  # Replace with actual property ID

    # Create and run the scraper
    scraper = Scraper(url, property_id)
    scraper.scrape()
