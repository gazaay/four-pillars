import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create async engine for PostgreSQL
engine = create_async_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.API_DEBUG,
    pool_size=settings.DATABASE_MAX_CONNECTIONS,
    max_overflow=10,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create a base class for declarative models
Base = declarative_base()

async def init_db():
    """Initialize the database by creating all tables."""
    try:
        # Create tables that don't exist yet
        async with engine.begin() as conn:
            # Only for development - in production, use Alembic
            if settings.API_DEBUG:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created")
            
        logger.info("Database initialization successful")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def get_db():
    """
    Dependency function that yields a database session.
    Use this as a FastAPI dependency to get a database session.
    """
    async_session = AsyncSessionLocal()
    try:
        yield async_session
    finally:
        await async_session.close() 