import logging
from supabase_utils import supabase_client
from models.property import Property
from scraper import Scraper  # Adjust the import path if necessary
from typing import List, Optional
from uuid import UUID


class PropertyService:
    @staticmethod
    def create_property(property_data: Property) -> Property:
        try:
            # Convert the Property model to a dictionary, excluding unset fields
            property_dict = property_data.dict(exclude_unset=True)

            # Insert the property into the 'properties' table
            response = (
                supabase_client.table("properties").insert(property_dict).execute()
            )
            if not response.data:
                logging.error("Failed to insert property: No data returned.")
                raise Exception("Failed to insert property: No data returned.")

            data = response.data[0]
            new_property = Property(**data)

            # Proceed to scrape if 'property_url' is provided
            if "property_url" in property_dict and property_dict["property_url"]:
                scraper = Scraper(property_dict["property_url"])
                scraped_data = scraper.scrape()

                if scraped_data:
                    # Save the scraped data using the scraper's save method
                    filename = scraper.save_scraped_data(new_property.id, scraped_data)
                    document_data = {
                        "property_id": new_property.id,
                        "file_url": filename,
                    }

                    # Insert the document into the 'documents' table
                    document_response = (
                        supabase_client.table("documents")
                        .insert(document_data)
                        .execute()
                    )
                    if filename:
                        logging.info(
                            f"Scraped data saved successfully for property {new_property.id}"
                        )
                    else:
                        logging.error(
                            f"Failed to save scraped data for property {new_property.id}"
                        )
                else:
                    logging.error(
                        f"Failed to scrape data for property {new_property.id}"
                    )
            else:
                logging.info(
                    f"No 'property_url' provided for property {new_property.id}"
                )

            return new_property

        except Exception as e:
            logging.error(f"Exception in create_property: {e}")
            raise e

    @staticmethod
    def get_property(property_id: UUID) -> Optional[Property]:
        try:
            response = (
                supabase_client.table("properties")
                .select("*")
                .eq("id", str(property_id))
                .execute()
            )
            if not response.data:
                logging.error(f"No property found with id: {property_id}")
                return None

            return Property(**response.data[0])

        except Exception as e:
            logging.error(f"Exception in get_property: {e}")
            raise e

    @staticmethod
    def update_property(
        property_id: UUID, update_data: dict, user_id: UUID
    ) -> Property:
        try:
            # Verify that the user is the owner of the property
            existing_property = PropertyService.get_property(property_id)
            if not existing_property:
                raise Exception("Property not found")
            if existing_property.owner_id != user_id:
                raise Exception("Unauthorized: You do not own this property")

            response = (
                supabase_client.table("properties")
                .update(update_data)
                .eq("id", str(property_id))
                .execute()
            )
            if not response.data:
                logging.error(
                    f"Failed to update property: No data returned for property {property_id}"
                )
                raise Exception("Property not found after update")

            return Property(**response.data[0])

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

            response = (
                supabase_client.table("properties")
                .delete()
                .eq("id", str(property_id))
                .execute()
            )
            if not response.data:
                logging.error(f"Failed to delete property {property_id}")
                raise Exception(f"Failed to delete property {property_id}")

            return True
        except Exception as e:
            logging.error(f"Exception in delete_property: {e}")
            raise e

    @staticmethod
    def list_properties(owner_id: Optional[UUID] = None) -> List[Property]:
        try:
            query = supabase_client.table("properties").select("*")
            if owner_id:
                query = query.eq("owner_id", str(owner_id))

            response = query.execute()
            if not response.data:
                logging.error("No properties found")
                return []

            properties = [Property(**prop) for prop in response.data]
            return properties
        except Exception as e:
            logging.error(f"Exception in list_properties: {e}")
            raise e
