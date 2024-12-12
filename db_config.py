import databases
import pydantic

import ormar
import sqlalchemy


DATABASE_URL = "postgresql://postgres.cjpqoecwszjepmrijxit:dU7FwqM2JowJt4r.V@VfodBAHP@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
base_ormar_config = ormar.OrmarConfig(
    database=databases.Database(DATABASE_URL),
    metadata=sqlalchemy.MetaData(),
    engine=sqlalchemy.create_engine(DATABASE_URL),
)


async def test_database_connection():
    """
    Test the database connection by attempting to connect and execute a simple query.
    Returns True if connection successful, False otherwise.
    """
    try:
        # Get database instance from base config
        database = base_ormar_config.database

        breakpoint()
        # Try connecting
        await database.connect()

        # Execute simple test query
        await database.fetch_one("SELECT 1")

        # Close connection
        await database.disconnect()

        return True

    except Exception as e:
        print(f"Database connection test failed: {str(e)}")
        return False
