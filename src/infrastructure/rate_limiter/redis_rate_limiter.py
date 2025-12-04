from typing import Optional

import redis.asyncio as aioredis

from core.settings import get_settings


class RedisRateLimiter:
    """
    Redis-based rate limiter using simple counter with expiration.
    """

    def __init__(self):
        """Initializes rate limiter with settings."""
        self.redis: Optional[aioredis.Redis] = None
        self.settings = get_settings()

    async def initialize(self) -> None:
        """Establishes connection to Redis server."""
        self.redis = await aioredis.from_url(
            self.settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def check_rate_limit(
            self,
            key: str,
            max_requests: Optional[int] = None,
            window_seconds: Optional[int] = None
    ) -> bool:
        """Checks if request is within rate limit for given key."""
        max_requests = max_requests or self.settings.rate_limit_max_requests
        window_seconds = window_seconds or self.settings.rate_limit_window_seconds

        rate_limit_key = f"rate_limit:{key}"

        current = await self.redis.get(rate_limit_key)

        if not current:
            await self.redis.setex(rate_limit_key, window_seconds, 1)
            return True

        if int(current) >= max_requests:
            return False

        await self.redis.incr(rate_limit_key)
        return True

    async def close(self) -> None:
        """Closes Redis connection."""
        if self.redis:
            await self.redis.close()


_rate_limiter: Optional[RedisRateLimiter] = None


async def get_rate_limiter() -> RedisRateLimiter:
    """Returns singleton rate limiter instance."""
    global _rate_limiter

    if not _rate_limiter:
        _rate_limiter = RedisRateLimiter()
        await _rate_limiter.initialize()

    return _rate_limiter
