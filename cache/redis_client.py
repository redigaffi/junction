import redis
from typing import Optional, Any
from typing import List

class RedisClient:
    _redis_client: Optional[redis.asyncio.Redis] = None

    @classmethod
    async def initialize(cls, redis_url="redis://localhost"):
        if cls._redis_client is None:
            cls._redis_client = redis.asyncio.Redis.from_url(redis_url)

    @classmethod
    async def close_connection(cls):
        if cls._redis_client:
            await cls._redis_client.close()
            cls._redis_client = None

    @classmethod
    async def set_json_value(cls, key: str, path: str, value: Any):
        if cls._redis_client is None:
            raise ValueError("Redis client is not initialized. Call initialize() first.")
        await cls._redis_client.json().set(key, path, value)

    @classmethod
    async def get_json_value(cls, key: str) -> Any:
        if cls._redis_client is None:
            raise ValueError("Redis client is not initialized. Call initialize() first.")

        return await cls._redis_client.json().get(key)

    @classmethod
    async def get_keys(cls, pattern: str) -> List[str]:
        if cls._redis_client is None:
            raise ValueError("Redis client is not initialized. Call initialize() first.")

        return await cls._redis_client.keys(pattern)

    @classmethod
    async def get_value(cls, key: str):
        if cls._redis_client is None:
            raise ValueError("Redis client is not initialized. Call initialize() first.")
        value = await cls._redis_client.get(key)
        return value.decode() if value else None