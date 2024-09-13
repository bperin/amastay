from utils import supabase
from typing import Optional

def create_property(name: str, address: str, external_url: str) -> Optional[dict]:
    """Creates a property entry for the logged-in owner."""
    
    # New property data
    new_property_data = {
        'name': name,
        'address': address,
        'external_url': external_url
    }

    # Insert the property into the properties table
    property_response = supabase.table('properties').insert(new_property_data).execute()
    
    return property_response.data[0] if property_response.data else None
