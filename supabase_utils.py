# supabase_utils.py

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

breakpoint()
# Create a Supabase client using the service role key for admin operations
supabase_admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Create another client with anon key for regular operations
supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
