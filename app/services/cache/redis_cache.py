# This module provides a simple interface for caching data in Redis.
import redis
import json
import os
from hashlib import md5

CACHE_7_DAYS = 7 * 24 * 60 * 60
CACHE_30_DAYS = 30 * 24 * 60 * 60
CACHE_90_DAYS = 90 * 24 * 60 * 60

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def build_cache_key(prefix: str, payload: dict):
    """
    Create deterministic cache key from request payload
    """
    raw = json.dumps(payload, sort_keys=True)
    hashed = md5(raw.encode()).hexdigest()
    return f"{prefix}:{hashed}"


def get_cache(key: str):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def set_cache(key: str, value: dict, ttl: int):
    redis_client.setex(
        key,
        ttl,
        json.dumps(value)
    )