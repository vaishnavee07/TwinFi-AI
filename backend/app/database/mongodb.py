from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_state = MongoDB()

async def connect_to_mongo():
    logger.info("Connecting to Cosmos DB / MongoDB...")
    db_state.client = AsyncIOMotorClient(
        settings.MONGO_URI,
        maxPoolSize=50,
        minPoolSize=10
    )
    db_state.db = db_state.client[settings.MONGO_DB_NAME]
    logger.info("Connected to Cosmos DB / MongoDB.")

async def close_mongo_connection():
    logger.info("Closing Cosmos DB / MongoDB connection...")
    if db_state.client:
        db_state.client.close()
    logger.info("Closed Cosmos DB / MongoDB connection.")

def get_mongo_db():
    """FastAPI Dependency to get MongoDB database instance"""
    return db_state.db
