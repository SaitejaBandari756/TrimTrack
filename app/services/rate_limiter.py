import time
import uuid
import logging
from typing import Optional

from app.services.cache_service import cache_service
from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    async def is_rate_limited(
        self,
        ip_address: str,
        endpoint_type: str = "redirect",
        limit: Optional[int] = None,
        window: Optional[int] = None,
    ) -> tuple[bool, int, int]:

        redis_client = cache_service.client
        if not redis_client:
            return False, 999, 0

        if limit is None:
            limit = (
                settings.rate_limit_create
                if endpoint_type == "create"
                else settings.rate_limit_redirect
            )
        if window is None:
            window = settings.rate_limit_window

        key = f"rl:{ip_address}:{endpoint_type}"
        now = time.time()
        window_start = now - window

        try:
            pipe = redis_client.pipeline(transaction=True)
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            member = f"{now}:{uuid.uuid4().hex[:8]}"
            pipe.zadd(key, {member: now})
            pipe.expire(key, window + 1)

            results = await pipe.execute()
            current_count = results[1]

            remaining = max(0, limit - current_count - 1)
            is_limited = current_count >= limit

            if is_limited:
                await redis_client.zrem(key, member)
                oldest = await redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(oldest[0][1] + window - now) + 1
                else:
                    retry_after = window
                return True, 0, retry_after

            return False, remaining, 0

        except Exception as e:
            logger.warning(f"Rate limiter error: {e}. Failing open.")
            return False, 999, 0


rate_limiter = RateLimiter()
