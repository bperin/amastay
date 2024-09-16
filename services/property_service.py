# services/property_service.py

from supabase_utils import supabase_client
from scraper import Scraper  # Import the Scraper class
import logging

class PropertyService:
    @staticmethod
    def create_property(property_data):
        """
        Creates a new property and invokes the scraper to scrape property data if a URL is provided.
        """
        try:
            logging.debug(f"Creating property with data: {property_data}")

            # Insert the property data into the 'properties' table
            response = supabase_client.table('properties').insert(property_data).execute()

            if response.error:
                logging.error(f"Error creating property: {response.error.message}")
                return {"error": response.error.message}

            # Fetch the property ID from the response
            property_id = response.data[0]['id']

            # Scrape the property URL if available
            if 'url' in property_data:
                scraper = Scraper(property_data['url'])
                scraped_data = scraper.scrape()

                if scraped_data:
                    # Save the scraped data to Supabase storage
                    filename = scraper.save_scraped_data(property_id, scraped_data)
                    if filename:
                        logging.info(f"Scraped data saved successfully for property {property_id}")
                    else:
                        logging.error(f"Failed to save scraped data for property {property_id}")
                else:
                    logging.error(f"Failed to scrape data for property {property_id}")

            return {"message": "Property created successfully", "property_id": property_id}

        except Exception as e:
            logging.error(f"Error creating property: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_properties():
        """
        Fetches the list of properties from the Supabase database.
        """
        try:
            logging.debug("Fetching properties from database...")

            # Fetch data from the Supabase 'properties' table
            response = supabase_client.table('properties').select('*').execute()

            # Check for errors in the response
            if response.error:
                logging.error(f"Error fetching properties: {response.error.message}")
                return {"error": response.error.message}

            logging.debug(f"Properties fetched: {response.data}")
            return response.data

        except Exception as e:
            logging.error(f"Error fetching properties: {e}")
            return {"error": str(e)}

    @staticmethod
    def update_property(property_id, property_data):
        """
        Updates a property in the database by property_id and invokes the scraper if a new URL is provided.
        """
        try:
            logging.debug(f"Updating property {property_id} with data {property_data}")

            # Perform the update in Supabase
            response = supabase_client.table('properties').update(property_data).eq('id', property_id).execute()

            if response.error:
                logging.error(f"Error updating property: {response.error.message}")
                return {"error": response.error.message}

            # If a new URL is provided, trigger the scraper
            if 'url' in property_data:
                scraper = Scraper(property_data['url'])
                scraped_data = scraper.scrape()

                if scraped_data:
                    # Save the scraped data to Supabase storage
                    filename = scraper.save_scraped_data(property_id, scraped_data)
                    if filename:
                        logging.info(f"Scraped data saved successfully for property {property_id}")
                    else:
                        logging.error(f"Failed to save scraped data for property {property_id}")
                else:
                    logging.error(f"Failed to scrape data for property {property_id}")

            return {"message": "Property updated successfully"}

        except Exception as e:
            logging.error(f"Error updating property: {e}")
            return {"error": str(e)}

    @staticmethod
    def delete_property(property_id):
        """
        Deletes a property from the database by property_id.
        """
        try:
            logging.debug(f"Deleting property {property_id}")

            # Perform the delete operation in Supabase
            response = supabase_client.table('properties').delete().eq('id', property_id).execute()

            if response.error:
                logging.error(f"Error deleting property: {response.error.message}")
                return {"error": response.error.message}

            logging.debug(f"Property {property_id} deleted successfully")
            return {"message": "Property deleted successfully"}

        except Exception as e:
            logging.error(f"Error deleting property: {e}")
            return {"error": str(e)}
