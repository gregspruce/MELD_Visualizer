"""
Cache service for storing and retrieving processed data.
Implements LRU cache with TTL for DataFrame operations.
"""

import time
import hashlib
import json
from typing import Any, Optional, Dict, Tuple
from collections import OrderedDict
import pandas as pd
import io
import logging

from constants import CACHE_TTL_SECONDS, MAX_CACHE_SIZE_MB

logger = logging.getLogger(__name__)


class CacheService:
    """
    In-memory cache for DataFrames and processing results.
    Uses LRU eviction and TTL expiration.
    """
    
    def __init__(self, max_size_mb: int = MAX_CACHE_SIZE_MB, ttl_seconds: int = CACHE_TTL_SECONDS):
        """
        Initialize cache service.
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.cache: OrderedDict[str, Tuple[Any, float, int]] = OrderedDict()
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        self.current_size_bytes = 0
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimate memory size of an object in bytes."""
        if isinstance(obj, pd.DataFrame):
            return obj.memory_usage(deep=True).sum()
        elif isinstance(obj, dict):
            # Rough estimate for dictionaries
            return len(json.dumps(obj, default=str).encode())
        else:
            # Rough estimate for other objects
            return len(str(obj).encode())
    
    def _evict_if_needed(self, required_size: int) -> None:
        """Evict old entries if cache size exceeds limit."""
        while self.current_size_bytes + required_size > self.max_size_bytes and self.cache:
            # Remove oldest entry (LRU)
            oldest_key = next(iter(self.cache))
            _, _, size = self.cache[oldest_key]
            del self.cache[oldest_key]
            self.current_size_bytes -= size
            logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache if it exists and hasn't expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, timestamp, size = self.cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            del self.cache[key]
            self.current_size_bytes -= size
            self.misses += 1
            logger.debug(f"Cache entry expired: {key}")
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Store item in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove old entry if exists
        if key in self.cache:
            _, _, old_size = self.cache[key]
            self.current_size_bytes -= old_size
        
        # Estimate size and evict if needed
        size = self._estimate_size(value)
        self._evict_if_needed(size)
        
        # Store new entry
        self.cache[key] = (value, time.time(), size)
        self.current_size_bytes += size
        logger.debug(f"Cached entry: {key} (size: {size} bytes)")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.current_size_bytes = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'entries': len(self.cache),
            'size_mb': self.current_size_bytes / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }
    
    def cache_dataframe(self, df: pd.DataFrame, identifier: str) -> str:
        """
        Cache a DataFrame with a specific identifier.
        
        Args:
            df: DataFrame to cache
            identifier: Unique identifier for this DataFrame
            
        Returns:
            Cache key for retrieval
        """
        key = f"df_{identifier}"
        # Store as JSON for efficient serialization
        df_json = df.to_json(date_format='iso', orient='split')
        self.set(key, df_json)
        return key
    
    def get_dataframe(self, identifier: str) -> Optional[pd.DataFrame]:
        """
        Retrieve a cached DataFrame.
        
        Args:
            identifier: DataFrame identifier
            
        Returns:
            DataFrame or None if not cached
        """
        key = f"df_{identifier}"
        df_json = self.get(key)
        
        if df_json is None:
            return None
        
        try:
            return pd.read_json(io.StringIO(df_json), orient='split')
        except Exception as e:
            logger.error(f"Failed to deserialize cached DataFrame: {e}")
            return None


# Global cache instance
_cache_instance = None


def get_cache() -> CacheService:
    """Get or create the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance


def cached(prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        prefix: Optional prefix for cache keys
        
    Example:
        @cached("parse")
        def parse_file(contents, filename):
            # expensive operation
            return result
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            key_parts = [prefix, func.__name__] if prefix else [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in kwargs.items()])
            key = cache._generate_key(*key_parts)
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return wrapper
    return decorator