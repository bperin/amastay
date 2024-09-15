from supabase_utils import supabase_client

class PropertyService:

    @staticmethod
    def create_property(name: str, address: str, external_url: str):
        """Creates a property entry in the database."""
        
        new_property_data = {
            'name': name,
            'address': address,
            'external_url': external_url
        }

        property_response = supabase_client.table('properties').insert(new_property_data).execute()
        return property_response.data[0] if property_response.data else None

    @staticmethod
    def get_properties():
        """Fetches all properties from the database."""
        
        property_response = supabase_client.table('properties').select('*').execute()
        return property_response.data if property_response.data else []
