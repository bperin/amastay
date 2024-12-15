# db_config.py
import os
import databases
import sqlalchemy
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL)


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
