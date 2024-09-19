import unittest
from scraper import Scraper
from supabase_utils import create_client
from generte_ai_response import generate_ai_response
import os

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class TestScraperIntegration(unittest.TestCase):

    def test_scrape_property_and_ask_ai(self):
        """
        Scrape the property, save it, and interact with AI
        """
        # Try to retrieve the property ID from Supabase
        result = supabase.from_('properties').select('id').eq('property_name', 'Airbnb Property Test').execute()

        # Check if the result is empty
        if len(result.data) == 0:
            self.fail("Property 'Airbnb Property Test' was not found in the properties table.")
        else:
            property_id = result.data[0]['id']

            # Scrape the property from Airbnb
            url = "https://www.airbnb.com/rooms/43623698"
            scraper = Scraper(url, property_id)
            document = scraper.scrape()

            # Verify scraping worked and document is uploaded
            self.assertIsNotNone(document)
            print(f"Scraped Document:\n{document}")

            # Interact with AI by passing the document
            question = "What is the nightly rate for this property?"
            ai_response = generate_ai_response(property_id, question)
            
            # Test the AI response (this will depend on the model's implementation)
            print(f"AI Response: {ai_response}")
            self.assertIsNotNone(ai_response)

if __name__ == '__main__':
    unittest.main()
