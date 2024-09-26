# property_service.py

import logging
from supabase_utils import supabase_client
from models.property import Property
from scraper import Scraper  # Adjust the import path if necessary
from typing import List, Optional
from uuid import UUID

class PropertyService:
    @staticmethod
    def create_property(property_data: Property, user_id: UUID) -> Property:
        try:
            # Convert the Property model to a dictionary, excluding unset fields
            property_dict = property_data.dict(exclude_unset=True)
            property_dict['owner_id'] = str(user_id)  # Ensure owner_id is a string

            # Insert the property into the 'properties' table
            response = supabase_client.table('properties').insert(property_dict).execute()
            if response.error:
                logging.error(f"Error inserting property: {response.error.message}")
                raise Exception(response.error.message)

            data = response.data[0]
            new_property = Property(**data)

            # If 'property_url' is provided, use the scraper
            if 'property_url' in property_dict and property_dict['property_url']:
                scraper = Scraper(property_dict['property_url'])
                scraped_data = scraper.scrape()

                if scraped_data:
                    # Save the scraped data using the scraper's save method
                    filename = scraper.save_scraped_data(new_property.id, scraped_data)
                    if filename:
                        logging.info(f"Scraped data saved successfully for property {new_property.id}")
                    else:
                        logging.error(f"Failed to save scraped data for property {new_property.id}")
                else:
                    logging.error(f"Failed to scrape data for property {new_property.id}")
            else:
                logging.info(f"No 'property_url' provided for property {new_property.id}")

            return new_property

        except Exception as e:
            logging.error(f"Exception in create_property: {e}")
            raise e

    @staticmethod
    def get_property(property_id: UUID) -> Optional[Property]:
        try:
            response = supabase_client.table('properties').select('*').eq('id', str(property_id)).execute()
            if response.error:
                logging.error(f"Error fetching property: {response.error.message}")
                raise Exception(response.error.message)

            if response.data:
                return Property(**response.data[0])
            else:
                return None
        except Exception as e:
            logging.error(f"Exception in get_property: {e}")
            raise e

    @staticmethod
    def update_property(property_id: UUID, update_data: dict, user_id: UUID) -> Property:
        try:
            # Verify that the user is the owner of the property
            existing_property = PropertyService.get_property(property_id)
            if not existing_property:
                raise Exception("Property not found")
            if existing_property.owner_id != user_id:
                raise Exception("Unauthorized: You do not own this property")

            response = supabase_client.table('properties').update(update_data).eq('id', str(property_id)).execute()
            if response.error:
                logging.error(f"Error updating property: {response.error.message}")
                raise Exception(response.error.message)

            if response.data:
                return Property(**response.data[0])
            else:
                raise Exception("Property not found after update")
        except Exception as e:
            logging.error(f"Exception in update_property: {e}")
            raise e

    @staticmethod
    def delete_property(property_id: UUID, user_id: UUID) -> bool:
        try:
            # Verify that the user is the owner of the property
            existing_property = PropertyService.get_property(property_id)
            if not existing_property:
                raise Exception("Property not found")
            if existing_property.owner_id != user_id:
                raise Exception("Unauthorized: You do not own this property")

            response = supabase_client.table('properties').delete().eq('id', str(property_id)).execute()
            if response.error:
                logging.error(f"Error deleting property: {response.error.message}")
                raise Exception(response.error.message)

            return True
        except Exception as e:
            logging.error(f"Exception in delete_property: {e}")
            raise e

    @staticmethod
    def list_properties(owner_id: Optional[UUID] = None) -> List[Property]:
        try:
            query = supabase_client.table('properties').select('*')
            if owner_id:
                query = query.eq('owner_id', str(owner_id))

            response = query.execute()
            if response.error:
                logging.error(f"Error listing properties: {response.error.message}")
                raise Exception(response.error.message)

            properties = [Property(**prop) for prop in response.data]
            return properties
        except Exception as e:
            logging.error(f"Exception in list_properties: {e}")
            raise e
