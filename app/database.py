"""
Database Module - Database initialization and management
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import config

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    config.DATABASE_URL,
    echo=config.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def drop_db():
    """Drop all tables (for testing)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop database: {str(e)}")
        raise


def reset_db():
    """Reset database (drop and recreate)"""
    drop_db()
    init_db()
    logger.info("Database reset successfully")

