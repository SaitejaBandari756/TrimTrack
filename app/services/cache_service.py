import redis.asyncio as redis
import json
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:

    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def connect(self):
        try:
            self._redis = redis.from_url(
                settings.redis_url,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True,
            )
            await self._redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Cache will be unavailable.")
            self._redis = None

    async def disconnect(self):
        if self._redis:
            await self._redis.close()
            logger.info("Redis disconnected")

    @property
    def is_connected(self) -> bool:
        return self._redis is not None

    async def get_url(self, short_code: str) -> Optional[str]:

        if not self._redis:
            return None
        try:
            result = await self._redis.get(f"url:{short_code}")
            if result:
                logger.debug(f"Cache HIT for {short_code}")
            else:
                logger.debug(f"Cache MISS for {short_code}")
            return result
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None

    async def set_url(self, short_code: str, long_url: str, ttl: int = None):

        if not self._redis:
            return
        try:
            ttl = ttl or settings.cache_ttl
            await self._redis.set(f"url:{short_code}", long_url, ex=ttl)
            logger.debug(f"Cached {short_code} with TTL={ttl}s")
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    async def delete_url(self, short_code: str):
        if not self._redis:
            return
        try:
            await self._redis.delete(f"url:{short_code}")
            # Also delete QR cache
            await self._redis.delete(f"qr:{short_code}")
            logger.debug(f"Cache invalidated for {short_code}")
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")

    async def get_url_metadata(self, short_code: str) -> Optional[dict]:
        if not self._redis:
            return None
        try:
            data = await self._redis.get(f"meta:{short_code}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning(f"Cache metadata get failed: {e}")
            return None

    async def set_url_metadata(self, short_code: str, metadata: dict, ttl: int = None):
        if not self._redis:
            return
        try:
            ttl = ttl or settings.cache_ttl
            await self._redis.set(
                f"meta:{short_code}", json.dumps(metadata, default=str), ex=ttl
            )
        except Exception as e:
            logger.warning(f"Cache metadata set failed: {e}")

    async def set_qr(self, short_code: str, qr_base64: str, ttl: int = None):
        if not self._redis:
            return
        try:
            ttl = ttl or settings.cache_ttl
            await self._redis.set(f"qr:{short_code}", qr_base64, ex=ttl)
        except Exception as e:
            logger.warning(f"QR cache set failed: {e}")

    async def get_qr(self, short_code: str) -> Optional[str]:
        if not self._redis:
            return None
        try:
            return await self._redis.get(f"qr:{short_code}")
        except Exception as e:
            logger.warning(f"QR cache get failed: {e}")
            return None

    async def health_check(self) -> bool:
        if not self._redis:
            return False
        try:
            await self._redis.ping()
            return True
        except Exception:
            return False

    @property
    def client(self) -> Optional[redis.Redis]:
        return self._redis


# Module-level singleton
cache_service = CacheService()
