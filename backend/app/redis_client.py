import redis.asyncio as redis_async
from app.config import settings
import json

redis = redis_async.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
    yield redis

async def publish_event(channel: str, data: dict):
    await redis.publish(channel, json.dumps(data))
