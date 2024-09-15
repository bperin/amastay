from scraper import Scraper
from supabase_utils import supabase_client

class PropertyService:

    @staticmethod
    def create_property(name: str, address: str, external_url: str):
        """Creates a property entry in the database and invokes the scraper."""
        
        new_property_data = {
            'name': name,
            'address': address,
            'external_url': external_url
        }

        # Insert the new property into the database
        property_response = supabase_client.table('properties').insert(new_property_data).execute()
        created_property = property_response.data[0] if property_response.data else None
        
        if created_property:
            # Invoke the scraper to scrape the external URL and save the data
            scraper = Scraper(external_url)
            scraped_data = scraper.scrape()
            
            if scraped_data:
                # Save the scraped data (you can choose where to save it: Supabase storage or in the properties table)
                scraper.save_scraped_data(created_property['id'], scraped_data)

        return created_property

    @staticmethod
    def get_properties():
        """Fetches all properties from the database."""
        
        property_response = supabase_client.table('properties').select('*').execute()
        return property_response.data if property_response.data else []
