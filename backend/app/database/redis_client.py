import redis.asyncio as redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    client: redis.Redis = None

redis_state = RedisCache()

async def connect_to_redis():
    logger.info("Connecting to Azure Redis Cache...")
    redis_state.client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    logger.info("Connected to Azure Redis Cache.")

async def close_redis_connection():
    logger.info("Closing Redis connection...")
    if redis_state.client:
        await redis_state.client.close()
    logger.info("Closed Redis connection.")

def get_redis():
    """FastAPI Dependency to get Redis client"""
    return redis_state.client
