import os
from databases import Database
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv(override=True)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Use async PostgreSQL driver
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("connecting to", DATABASE_URL)

# Create async SQLAlchemy components
metadata = MetaData()
database = Database(DATABASE_URL)

# Create async engine
engine = create_async_engine(DATABASE_URL, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800, echo=True)

# Create async session factory
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False)


async def get_session() -> AsyncSession:
    try:
        async with SessionLocal() as session:
            yield session
    except Exception as e:
        print(f"Session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


async def connect_to_database():
    await database.connect()


async def close_database_connection():
    await database.disconnect()
