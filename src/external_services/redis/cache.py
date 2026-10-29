import hashlib
import json
from datetime import date, datetime, time
from typing import Any, Dict, Optional

from fastapi import Request
from redis.asyncio import Redis


def json_serializer(obj: Any) -> Any:
    """Serializer"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.isoformat()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    raise TypeError(f"Type {type(obj)} not serializable")


class CacheService:

    def __init__(self, redis: Redis, prefix: str):
        self.redis = redis
        self.prefix = prefix

    def _hash_params(self, params: Dict[str, Any]) -> str:
        """Hashing request params"""
        param_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(param_str.encode()).hexdigest()

    async def get(self, key: str) -> Optional[dict]:
        data = await self.redis.get(f"{self.prefix}{key}")
        return json.loads(data) if data else None

    async def set(self, key: str, data: dict, ttl: int = 300):
        await self.redis.setex(f"{self.prefix}{key}", ttl, json.dumps(data))

    async def get_list_cache(self, params: Dict[str, Any]) -> Optional[dict]:
        key = f"{self.prefix}:list:{self._hash_params(params)}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set_list_cache(self, params: Dict[str, Any], data: dict, ttl: int = 300):
        key = f"{self.prefix}:list:{self._hash_params(params)}"
        serialized = json.dumps(data, default=json_serializer, ensure_ascii=False)
        await self.redis.setex(key, ttl, serialized)

    async def invalidate_list_cache(self):
        """Invalidation of cache for paginated elements"""
        keys = await self.redis.keys(f"{self.prefix}:*")
        if keys:
            await self.redis.delete(*keys)

    async def delete(self, pattern: str):
        keys = await self.redis.keys(f"{self.prefix}{pattern}")
        if keys:
            await self.redis.delete(*keys)

    @staticmethod
    def pagination_key(request: Request) -> str:
        """Pagination key generator"""
        params = dict(request.query_params)
        return f"page:{params.get('page',1)}:size:{params.get('size',10)}"

    @staticmethod
    def search_key(request: Request) -> str:
        """Search and Pagination key generator"""
        params = dict(request.query_params)
        return f"search:{params.get('q')}:page:{params.get('page',1)}:size:{params.get('size',10)}"
