# create_property.py
from utils import supabase
from typing import Optional

def create_property(owner_id: str, property_name: str, address: str, city: str, state: str, zip_code: str, url: str) -> Optional[dict]:
    """Creates a property (rental) entry for the owner."""
    new_property_data = {
        'owner_id': owner_id,
        'property_name': property_name,
        'address': address,
        'city': city,
        'state': state,
        'zip': zip_code,
        'property_url': url
    }

    # Insert property into the properties table
    property_response = supabase.table('properties').insert(new_property_data).execute()
    
    return property_response.data[0] if property_response.data else None

# Example usage
if __name__ == "__main__":
    owner_id = "owner-uuid-1234"
    property_name = "Beautiful Beach House"
    address = "123 Ocean Ave"
    city = "Santa Monica"
    state = "CA"
    zip_code = "90401"
    url = "https://example.com/property-details"

    new_property = create_property(owner_id, property_name, address, city, state, zip_code, url)
    print(f"Property created: {new_property}")
