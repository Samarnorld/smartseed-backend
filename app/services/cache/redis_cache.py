# This module provides a simple interface for caching data in Redis.
import redis
import json
import os
import logging
from hashlib import md5

logger = logging.getLogger(__name__)

CACHE_1_HOUR = 60 * 60
CACHE_7_DAYS = 7 * 24 * 60 * 60
CACHE_30_DAYS = 30 * 24 * 60 * 60
CACHE_90_DAYS = 90 * 24 * 60 * 60

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_SSL = os.getenv("REDIS_SSL", "false").lower() == "true"
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Build Redis connection with security
redis_kwargs = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": REDIS_DB,
    "decode_responses": False,  # Keep binary for security
    "socket_connect_timeout": 5,
    "socket_keepalive": True,
    "health_check_interval": 30,
}

if REDIS_PASSWORD:
    redis_kwargs["password"] = REDIS_PASSWORD
    logger.info("Redis authentication enabled")

if REDIS_SSL:
    redis_kwargs["ssl"] = True
    redis_kwargs["ssl_certfile"] = os.getenv("REDIS_CERT_FILE")
    logger.info("Redis SSL enabled")

try:
    redis_client = redis.Redis(**redis_kwargs)
    # Test connection
    redis_client.ping()
    logger.info(f"Redis connected: {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {e}")
    # In production, this should fail hard
    # For now, redis operations will fail gracefully
    redis_client = None

def build_cache_key(prefix: str, payload: dict):
    """
    Create deterministic cache key from request payload.
    Uses MD5 hash for security and collision resistance.
    """
    try:
        raw = json.dumps(payload, sort_keys=True)
        hashed = md5(raw.encode()).hexdigest()
        return f"{prefix}:{hashed}"
    except Exception as e:
        logger.error(f"Failed to build cache key: {e}")
        return None


def get_cache(key: str):
    """Retrieve cached value. Returns None if not found or Redis unavailable."""
    if not redis_client or not key:
        return None
    
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data.decode() if isinstance(data, bytes) else data)
    except redis.ConnectionError:
        logger.warning("Redis connection lost, cache retrieval failed")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode cache data: {e}")
    except Exception as e:
        logger.error(f"Cache get error: {e}")
    
    return None


def set_cache(key: str, value: dict, ttl: int):
    """Set cached value with TTL. Fails gracefully if Redis unavailable."""
    if not redis_client or not key:
        return False
    
    try:
        json_data = json.dumps(value)
        redis_client.setex(
            key,
            ttl,
            json_data.encode() if isinstance(json_data, str) else json_data
        )
        return True
    except redis.ConnectionError:
        logger.warning("Redis connection lost, cache write failed")
    except json.JSONEncodeError as e:
        logger.error(f"Failed to encode cache data: {e}")
    except Exception as e:
        logger.error(f"Cache set error: {e}")
    
    return False