import json
import os

import redis

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    db=int(os.getenv("REDIS_DB", "0")),
    decode_responses=True,
)


def get_cache(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def set_cache(key, value, ttl=300):
    redis_client.set(key, json.dumps(value), ex=ttl)
