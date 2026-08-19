import redis.asyncio as redis

from src.backend.core.settings import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
