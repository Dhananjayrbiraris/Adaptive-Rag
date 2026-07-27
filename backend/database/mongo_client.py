"""
MongoDB client initialization with connection management.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config.settings import settings

logger = logging.getLogger(__name__)

MONGO_URL = settings.MONGODB_URL
DB_NAME = settings.MONGODB_DB_NAME

# Create client with connection pool settings
client = AsyncIOMotorClient(
    MONGO_URL,
    maxPoolSize=50,
    minPoolSize=10,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=20000,
)
db = client[DB_NAME]


async def verify_connection() -> bool:
    """
    Verify MongoDB connection is working.
    
    Returns:
        True if connection is successful, False otherwise.
    """
    try:
        await client.admin.command('ping')
        logger.info("MongoDB connection verified")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection verification failed: {e}")
        return False


def close_connection():
    """Close MongoDB client connection."""
    client.close()
    logger.info("MongoDB connection closed")
