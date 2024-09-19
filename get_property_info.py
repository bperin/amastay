import supabase_utils
from typing import Optional

def get_property_info(property_id: int) -> Optional[dict]:
    """Fetches property information based on the property ID."""
    response = supabase_utils.table('properties').select('*').eq('id', property_id).execute()
    
    if response.data:
        property_data = response.data[0]
        return {
            "name": property_data['property_name'],
            "address": f"{property_data['address']}, {property_data['city']}, {property_data['state']} {property_data['zip']}",
            "description": property_data['description'],
            "document": "General property info document (amenities, policies, etc.)"  # Placeholder document info
        }
    
    return None

# Example usage
if __name__ == "__main__":
    property_id = 1
    property_info = get_property_info(property_id)
    print(f"Property Info: {property_info}")
