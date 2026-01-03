from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

class Base(DeclarativeBase):
    pass

# Create engine once to avoid multiple engine instances
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL logging during development
    pool_pre_ping=True,  # Validates connections before use (essential for Neon)
    pool_size=20,  # Connection pool size
    max_overflow=50,  # Maximum overflow connections
    pool_recycle=300,  # Recycle connections after 5 minutes
    pool_timeout=30,  # Connection timeout
    connect_args={
        "server_settings": {
            "application_name": "robotics-book-app",
        },
    }
)

# Create async session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()