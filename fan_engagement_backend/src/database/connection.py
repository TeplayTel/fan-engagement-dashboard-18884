"""
Database connection module for Fan Engagement Backend

This module handles PostgreSQL database connections using SQLAlchemy,
including session management and connection pooling.
"""

import os
import logging
from typing import Generator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration from environment variables
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://appuser:dbuser123@localhost:5000/myapp")
POSTGRES_USER = os.getenv("POSTGRES_USER", "appuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "dbuser123") 
POSTGRES_DB = os.getenv("POSTGRES_DB", "myapp")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5000")

# Construct database URL if individual components are provided
if not POSTGRES_URL.startswith("postgresql://"):
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
else:
    DATABASE_URL = POSTGRES_URL

# SQLAlchemy engine configuration
ENGINE_CONFIG = {
    "poolclass": QueuePool,
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": os.getenv("DATABASE_ECHO", "false").lower() == "true"
}

# Create SQLAlchemy engine
try:
    engine = create_engine(DATABASE_URL, **ENGINE_CONFIG)
    logger.info(f"Database engine created successfully for: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

# Metadata for table introspection
metadata = MetaData()


class DatabaseManager:
    """
    Database manager class for handling connections and sessions
    """
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
        
    def get_engine(self):
        """
        Get the SQLAlchemy engine instance
        
        Returns:
            Engine: SQLAlchemy engine
        """
        return self.engine
    
    def create_tables(self):
        """
        Create all database tables based on models
        
        Note: This should be used with caution in production.
        Schema migrations should be handled separately.
        """
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self):
        """
        Drop all database tables
        
        WARNING: This will delete all data. Use only in development/testing.
        """
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            from sqlalchemy import text
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


# PUBLIC_INTERFACE
def get_database_session() -> Generator[Session, None, None]:
    """
    Dependency function to get database session for FastAPI endpoints
    
    This function creates a new database session for each request
    and ensures proper cleanup after the request is completed.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_database_session)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# PUBLIC_INTERFACE
def get_database_manager() -> DatabaseManager:
    """
    Get the global database manager instance
    
    Returns:
        DatabaseManager: Global database manager instance
    """
    return db_manager


# PUBLIC_INTERFACE
def init_database():
    """
    Initialize database connection and create tables if needed
    
    This function should be called during application startup
    to ensure database connectivity and table creation.
    """
    try:
        # Test connection
        if not db_manager.test_connection():
            raise Exception("Database connection failed")
        
        # Create tables (in production, use proper migrations)
        if os.getenv("CREATE_TABLES", "false").lower() == "true":
            db_manager.create_tables()
            logger.info("Database initialization completed")
        else:
            logger.info("Database connection established (table creation skipped)")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


# Context manager for database sessions
class DatabaseSession:
    """
    Context manager for database sessions
    
    Example:
        with DatabaseSession() as db:
            # Use db session here
            pass
    """
    
    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.db.rollback()
        else:
            self.db.commit()
        self.db.close()


# Utility functions for common database operations
# PUBLIC_INTERFACE
def execute_raw_sql(sql: str, params: dict = None) -> list:
    """
    Execute raw SQL query and return results
    
    Args:
        sql (str): SQL query to execute
        params (dict, optional): Query parameters
        
    Returns:
        list: Query results
        
    WARNING: Use with caution to avoid SQL injection
    """
    try:
        from sqlalchemy import text
        with DatabaseSession() as db:
            if params:
                result = db.execute(text(sql), params)
            else:
                result = db.execute(text(sql))
            return result.fetchall()
    except Exception as e:
        logger.error(f"Raw SQL execution failed: {e}")
        raise


# PUBLIC_INTERFACE
def get_database_info() -> dict:
    """
    Get database connection information (without sensitive data)
    
    Returns:
        dict: Database connection info
    """
    return {
        "database": POSTGRES_DB,
        "host": DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'localhost',
        "port": POSTGRES_PORT,
        "user": POSTGRES_USER,
        "engine_pool_size": ENGINE_CONFIG["pool_size"],
        "engine_max_overflow": ENGINE_CONFIG["max_overflow"]
    }


if __name__ == "__main__":
    # Test database connection when run directly
    print("Testing database connection...")
    try:
        init_database()
        info = get_database_info()
        print(f"Database info: {info}")
        print("Database connection test completed successfully!")
    except Exception as e:
        print(f"Database connection test failed: {e}")
