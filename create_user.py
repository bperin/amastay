# create_user.py
from utils import supabase
from typing import Optional

def create_or_get_user(phone_number: str, role: str = 'renter') -> Optional[dict]:
    """Creates or fetches a user profile based on the phone number."""
    # Check if the user already exists
    response = supabase.table('users').select('*').eq('phone_number', phone_number).execute()

    if response.data:
        return response.data[0]  # Return the existing user profile

    # If user doesn't exist, create a new user
    new_user_data = {
        'phone_number': phone_number,
        'user_role': role  # 'renter' or 'owner'
    }
    user_response = supabase.table('users').insert(new_user_data).execute()

    return user_response.data[0]

# Example usage
if __name__ == "__main__":
    phone_number = "+1234567890"
    user = create_or_get_user(phone_number)
    print(f"User created or fetched: {user}")
