import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (replace with your own database credentials)
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "db_name")
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy async engine
async_engine = create_async_engine(DATABASE_URL, future=True, echo=True)

# Create a configured "AsyncSession" class
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False  # Keeps objects active after commit
)

# Create a base class for declarative models
Base = declarative_base()


# Dependency to get an async database session
async def get_db_async() -> AsyncSession:
    async with AsyncSessionLocal() as db:  # Async context manager
        try:
            yield db  # Yield the session to the request
        except Exception:
            await db.rollback()  # Rollback if an error occurs
            raise
        finally:
            await db.close()  # Ensure the session is closed
