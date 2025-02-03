# supabase_utils.py

from dotenv import load_dotenv
import os
from supabase import create_client, Client
from gotrue import SyncSingleStoreGoTrueClient
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add console handler if not already present
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Get URL and keys from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
logger.info(f"Initializing Supabase client with URL: {SUPABASE_URL}")

SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
logger.debug(f"Using ANON_KEY starting with: {SUPABASE_ANON_KEY[:10]}...")

try:
    # Create basic client
    logger.debug("Creating Supabase client...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    logger.info("Supabase client created successfully")

    # Get auth client
    logger.debug("Getting auth client...")
    auth: SyncSingleStoreGoTrueClient = supabase.auth
    logger.info("Auth client initialized")

except Exception as e:
    logger.error(f"Failed to initialize Supabase: {str(e)}", exc_info=True)
    raise
