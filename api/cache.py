"""
Advanced Redis caching system with decorators and cache management.
"""
import json
import hashlib
from typing import Any, Callable, Optional
from functools import wraps
import redis
from datetime import timedelta

from settings import REDIS_URL
from logger import app_logger, log_with_context


class RedisCache:
    """
    Advanced Redis cache manager with TTL, namespacing, and invalidation.
    """

    def __init__(self, redis_url: str = None, default_ttl: int = 3600):
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds (1 hour)
        """
        self.redis_url = redis_url or REDIS_URL
        self.default_ttl = default_ttl
        self._client = None

    @property
    def client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                self._client.ping()
                app_logger.info("Redis cache initialized")
            except Exception as e:
                log_with_context(
                    app_logger,
                    "warning",
                    "Redis cache unavailable",
                    error=str(e)
                )
                self._client = None
        return self._client

    def _make_key(self, namespace: str, key: str) -> str:
        """
        Create a namespaced cache key.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            Namespaced key
        """
        return f"cache:{namespace}:{key}"

    def _serialize(self, value: Any) -> str:
        """
        Serialize value to JSON string.

        Args:
            value: Value to serialize

        Returns:
            JSON string
        """
        return json.dumps(value, default=str)

    def _deserialize(self, value: str) -> Any:
        """
        Deserialize JSON string to value.

        Args:
            value: JSON string

        Returns:
            Deserialized value
        """
        return json.loads(value)

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self.client:
            return None

        try:
            cache_key = self._make_key(namespace, key)
            value = self.client.get(cache_key)

            if value:
                log_with_context(
                    app_logger,
                    "debug",
                    "Cache hit",
                    namespace=namespace,
                    key=key
                )
                return self._deserialize(value)

            log_with_context(
                app_logger,
                "debug",
                "Cache miss",
                namespace=namespace,
                key=key
            )
            return None

        except Exception as e:
            log_with_context(
                app_logger,
                "error",
                "Cache get error",
                namespace=namespace,
                key=key,
                error=str(e)
            )
            return None

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            serialized = self._serialize(value)
            ttl = ttl or self.default_ttl

            self.client.setex(cache_key, ttl, serialized)

            log_with_context(
                app_logger,
                "debug",
                "Cache set",
                namespace=namespace,
                key=key,
                ttl=ttl
            )
            return True

        except Exception as e:
            log_with_context(
                app_logger,
                "error",
                "Cache set error",
                namespace=namespace,
                key=key,
                error=str(e)
            )
            return False

    def delete(self, namespace: str, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            self.client.delete(cache_key)

            log_with_context(
                app_logger,
                "debug",
                "Cache delete",
                namespace=namespace,
                key=key
            )
            return True

        except Exception as e:
            log_with_context(
                app_logger,
                "error",
                "Cache delete error",
                namespace=namespace,
                key=key,
                error=str(e)
            )
            return False

    def delete_pattern(self, namespace: str, pattern: str = "*") -> int:
        """
        Delete all keys matching a pattern in namespace.

        Args:
            namespace: Cache namespace
            pattern: Key pattern (supports *)

        Returns:
            Number of keys deleted
        """
        if not self.client:
            return 0

        try:
            cache_pattern = self._make_key(namespace, pattern)
            keys = self.client.keys(cache_pattern)

            if keys:
                deleted = self.client.delete(*keys)
                log_with_context(
                    app_logger,
                    "info",
                    "Cache pattern delete",
                    namespace=namespace,
                    pattern=pattern,
                    deleted=deleted
                )
                return deleted

            return 0

        except Exception as e:
            log_with_context(
                app_logger,
                "error",
                "Cache pattern delete error",
                namespace=namespace,
                pattern=pattern,
                error=str(e)
            )
            return 0

    def exists(self, namespace: str, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        if not self.client:
            return False

        try:
            cache_key = self._make_key(namespace, key)
            return bool(self.client.exists(cache_key))
        except Exception:
            return False

    def ttl(self, namespace: str, key: str) -> int:
        """
        Get remaining TTL for a key.

        Args:
            namespace: Cache namespace
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiry, -2 if not exists
        """
        if not self.client:
            return -2

        try:
            cache_key = self._make_key(namespace, key)
            return self.client.ttl(cache_key)
        except Exception:
            return -2


# Global cache instance
cache = RedisCache()


def cached(
    namespace: str,
    ttl: int = 3600,
    key_func: Optional[Callable] = None
):
    """
    Decorator to cache function results.

    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        key_func: Custom function to generate cache key from args

    Returns:
        Decorated function

    Example:
        @cached(namespace="users", ttl=300)
        def get_user(user_id: int):
            return fetch_from_db(user_id)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: hash of function name + args + kwargs
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                key_str = ":".join(key_parts)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()

            # Try to get from cache
            cached_value = cache.get(namespace, cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(namespace, cache_key, result, ttl=ttl)

            return result

        # Add cache management methods
        wrapper.cache_delete = lambda *args, **kwargs: cache.delete(
            namespace,
            key_func(*args, **kwargs) if key_func else hashlib.md5(
                ":".join([func.__name__] + [str(a) for a in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]).encode()
            ).hexdigest()
        )

        wrapper.cache_clear = lambda: cache.delete_pattern(namespace, "*")

        return wrapper

    return decorator


def invalidate_cache(namespace: str, pattern: str = "*"):
    """
    Invalidate cache for a namespace and pattern.

    Args:
        namespace: Cache namespace
        pattern: Key pattern to invalidate

    Returns:
        Number of keys deleted
    """
    return cache.delete_pattern(namespace, pattern)
