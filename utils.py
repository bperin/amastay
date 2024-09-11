# utils.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def scrape_property_data(url):
    """
    Scrapes property data from a given URL.
    """
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract relevant data (you'll need to adjust these based on the actual page structure)
        property_name = soup.find('h1').get_text()
        price_per_night = soup.find(class_='price').get_text()
        location = soup.find(class_='location').get_text()
        description = soup.find(class_='description').get_text()

        # Return the scraped data
        return {
            'name': property_name,
            'price_per_night': price_per_night,
            'location': location,
            'description': description
        }
    except Exception as e:
        raise Exception(f"Error scraping the property data: {str(e)}")
