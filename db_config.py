import os
import databases

import ormar
import sqlalchemy
import dotenv

dotenv.load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://postgres.cjpqoecwszjepmrijxit:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


base_ormar_config = ormar.OrmarConfig(
    database=databases.Database(DATABASE_URL),
    metadata=sqlalchemy.MetaData(),
    engine=sqlalchemy.create_engine(DATABASE_URL),
)


async def connect_to_database():
    await base_ormar_config.database.connect()


async def test_database_connection():
    """
    Test the database connection by attempting to connect and execute a simple query.
    Returns True if connection successful, False otherwise.
    """
    try:
        # Get database instance from base config
        database = base_ormar_config.database

        # Execute a simple query to test the connection
        query = "SELECT current_timestamp"
        result = await database.fetch_one(query)
        print(f"Database query result: {result}")

    except Exception as e:
        print(f"Database connection test failed: {str(e)}")
        return False


async def close_database_connection():
    """
    Close the database connection.
    """
    await base_ormar_config.database.disconnect()
