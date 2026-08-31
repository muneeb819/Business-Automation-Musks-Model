import redis.asyncio as redis
from app.core.config import settings
import json
from typing import Any, Optional

redis_client = None


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return redis_client


async def cache_set(key: str, value: Any, expire: int = 3600) -> None:
    client = await get_redis()
    await client.set(key, json.dumps(value), ex=expire)


async def cache_get(key: str) -> Optional[Any]:
    client = await get_redis()
    value = await client.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_delete(key: str) -> None:
    client = await get_redis()
    await client.delete(key)


async def cache_ttl(key: str) -> Optional[int]:
    client = await get_redis()
    return await client.ttl(key)


async def rate_limit(key: str, limit: int = 100, window: int = 3600) -> bool:
    client = await get_redis()
    current = await client.incr(key)
    if current == 1:
        await client.expire(key, window)
    return current <= limit


async def acquire_lock(key: str, timeout: int = 10) -> bool:
    client = await get_redis()
    result = await client.set(f"lock:{key}", "1", nx=True, ex=timeout)
    return bool(result)


async def release_lock(key: str) -> None:
    client = await get_redis()
    await client.delete(f"lock:{key}")
