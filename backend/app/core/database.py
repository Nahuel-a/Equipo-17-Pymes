from core.config import get_settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

settings = get_settings()

# Build the PostgreSQL database URL using the environment settings.
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

async_engine = create_async_engine(url=SQLALCHEMY_DATABASE_URL)

# Define a local asynchronous session to interact with the database.
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


# Define a base class for SQLAlchemy models.
class Base(DeclarativeBase):
    pass
