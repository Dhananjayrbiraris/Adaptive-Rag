"""
MongoDB client initialization.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from backend.config.settings import settings

MONGO_URL = settings.MONGODB_URL
DB_NAME = settings.MONGODB_DB_NAME

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
