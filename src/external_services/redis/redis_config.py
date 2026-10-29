from redis.asyncio import ConnectionPool

from src.config.settings import settings

CACHE_PREFIX = "app:cache:"
RATE_LIMIT_PREFIX = "app:rate_limit:"
DEFAULT_CACHE_TTL = 3000
SEARCH_CACHE_TTL = 60


redis_pool = ConnectionPool.from_url(settings.REDIS_URL)
