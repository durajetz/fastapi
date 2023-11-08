# core/redis_client.py

import redis
from ..core.config import settings


class RedisClient:

    def __init__(self, host: str):
        self.client = redis.Redis(
            host=host,
            decode_responses=True
        )

    def set(self, key: str, value: str):
        self.client.set(key, value)

    def get(self, key: str):
        return self.client.get(key)

    def exists(self, key: str):
        return self.client.exists(key)
