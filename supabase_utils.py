# supabase_utils.py

import os
from supabase import create_client

# These should now come from environment variables set by Copilot
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

# Create clients
supabase_admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
