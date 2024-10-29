import os
from dotenv import load_dotenv
import stripe

# Load environment variables
load_dotenv()

# Initialize Stripe client with API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Configure Stripe API version (optional but recommended)
stripe.api_version = "2023-10-16"  # Use latest stable version

# Create client instance
stripe_client = stripe.Client()
