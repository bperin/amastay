from utils import supabase
from typing import Optional

def create_property(name: str, address: str, external_url: str) -> Optional[dict]:
    """Creates a property (rental) entry for the logged-in owner."""
    
    # New property data without explicitly passing owner_id
    new_property_data = {
        'name': name,
        'address': address,
        'external_url': external_url
    }

    # Insert property into the properties table
    property_response = supabase.table('properties').insert(new_property_data).execute()
    
    return property_response.data[0] if property_response.data else None

# Example usage
if __name__ == "__main__":
    name = "Beautiful Beach House"
    address = "123 Ocean Ave"
    external_url = "https://example.com/property-details"

    new_property = create_property(name, address, external_url)
    
    if new_property:
        print(f"Property created: {new_property}")
    else:
        print("Failed to create property.")
