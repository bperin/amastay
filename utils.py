# utils.py
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_ROLE = os.getenv('SUPABASE_SERVICE_ROLE')

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)