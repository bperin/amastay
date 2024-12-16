# db_config.py
import os
import databases
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")  # db.cjpqoecwszjepmrijxit.supabase.co
DB_PORT = os.getenv("DB_PORT")  # 5432
DB_USER = os.getenv("DB_USER")  # postgres
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")  # postgres

# For Supabase, we need to include the project reference in the username
SUPABASE_PROJECT_REF = "cjpqoecwszjepmrijxit"  # This is from your DB_HOST
FULL_DB_USER = f"{DB_USER}.{SUPABASE_PROJECT_REF}"

# Direct connection URL format for Supabase with modified username
DATABASE_URL = f"postgresql://{FULL_DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Debug print to verify the URL (remove in production)
print(f"Connecting to: {DATABASE_URL}")

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(
    DATABASE_URL,
    # Add these parameters for better connection handling
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)


# Initialize Ormar's base configuration
class BaseOrmarConfig:
    metadata = metadata
    database = database
    engine = engine


base_ormar_config = BaseOrmarConfig()


# Functions to manage the database connection
async def connect_to_database():
    await database.connect()


async def close_database_connection():
    await database.disconnect()


async def test_database_connection():
    try:
        query = "SELECT current_timestamp"
        result = await database.fetch_one(query)
        print(f"Database query result: {result}")
        return True
    except Exception as e:
        print(f"Database connection test failed: {str(e)}")
        return False
