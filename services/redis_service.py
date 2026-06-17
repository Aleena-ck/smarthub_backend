# services/redis_service.py

import redis.asyncio as redis
import os
import json
from typing import Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = None

async def get_redis_client():
    """Get or create Redis client (optional)"""
    global redis_client
    if not redis_client:
        try:
            # Remove timeout parameter that's causing issues
            redis_client = await redis.from_url(REDIS_URL, decode_responses=True)
            await redis_client.ping()
            print("✅ Redis connected successfully")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            redis_client = None
            # Don't raise, just return None
    return redis_client

async def get_cache(key: str) -> Optional[str]:
    """Get value from cache (if Redis available)"""
    try:
        client = await get_redis_client()
        if client:
            return await client.get(key)
    except Exception:
        pass
    return None

async def set_cache(key: str, value: str, ttl: int = 300):
    """Set cache value with TTL (if Redis available)"""
    try:
        client = await get_redis_client()
        if client:
            await client.setex(key, ttl, value)
    except Exception:
        pass

async def delete_cache(key: str):
    """Delete cache key (if Redis available)"""
    try:
        client = await get_redis_client()
        if client:
            await client.delete(key)
    except Exception:
        pass

async def invalidate_dashboard_cache(user_id):
    """Invalidate all dashboard caches for a user (if Redis available)"""
    try:
        client = await get_redis_client()
        if client:
            pattern = f"dashboard:{user_id}:*"
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
    except Exception:
        pass