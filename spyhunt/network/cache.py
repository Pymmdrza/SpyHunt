"""
Response caching system for HTTP requests.
"""

import time
import hashlib
import pickle
from typing import Optional, Dict, Any
from threading import RLock
from pathlib import Path

from ..core.logger import get_logger
from ..core.config import get_config


class ResponseCache:
    """
    Thread-safe response cache with TTL support.
    Supports both memory and disk caching.
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 3600,
        disk_cache: bool = False,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize response cache.
        
        Args:
            max_size: Maximum number of cached responses
            default_ttl: Default time-to-live in seconds
            disk_cache: Whether to use disk caching
            cache_dir: Directory for disk cache
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.disk_cache = disk_cache
        
        # Memory cache
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()
        
        # Disk cache setup
        if disk_cache:
            config = get_config()
            self.cache_dir = Path(cache_dir or config.get('app.data_directory')) / 'cache'
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None
        
        self.logger = get_logger("spyhunt.cache")
    
    def _generate_key(self, url: str, method: str = 'GET', params: Optional[dict] = None) -> str:
        """Generate cache key for URL."""
        key_data = f"{method}:{url}"
        if params:
            key_data += f":{str(sorted(params.items()))}"
        
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _is_expired(self, entry: dict) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry['expires_at']
    
    def _cleanup_memory_cache(self) -> None:
        """Remove expired entries and enforce size limit."""
        now = time.time()
        
        # Remove expired entries
        expired_keys = [
            key for key, entry in self._memory_cache.items()
            if now > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._memory_cache[key]
        
        # Enforce size limit (LRU eviction)
        if len(self._memory_cache) > self.max_size:
            # Sort by last_accessed and remove oldest
            sorted_items = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1]['last_accessed']
            )
            
            items_to_remove = len(self._memory_cache) - self.max_size
            for key, _ in sorted_items[:items_to_remove]:
                del self._memory_cache[key]
    
    def _get_disk_cache_path(self, key: str) -> Path:
        """Get disk cache file path."""
        if not self.cache_dir:
            raise ValueError("Disk cache not enabled")
        return self.cache_dir / f"{key}.cache"
    
    def _load_from_disk(self, key: str) -> Optional[Any]:
        """Load cached response from disk."""
        if not self.disk_cache:
            return None
        
        cache_file = self._get_disk_cache_path(key)
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                entry = pickle.load(f)
            
            if self._is_expired(entry):
                cache_file.unlink(missing_ok=True)
                return None
            
            return entry['response']
            
        except Exception as e:
            self.logger.warning(f"Error loading disk cache: {e}")
            cache_file.unlink(missing_ok=True)
            return None
    
    def _save_to_disk(self, key: str, response: Any, ttl: int) -> None:
        """Save response to disk cache."""
        if not self.disk_cache:
            return
        
        try:
            entry = {
                'response': response,
                'cached_at': time.time(),
                'expires_at': time.time() + ttl,
                'last_accessed': time.time()
            }
            
            cache_file = self._get_disk_cache_path(key)
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
                
        except Exception as e:
            self.logger.warning(f"Error saving to disk cache: {e}")
    
    def get(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[dict] = None
    ) -> Optional[Any]:
        """
        Get cached response.
        
        Args:
            url: Request URL
            method: HTTP method
            params: Request parameters
            
        Returns:
            Cached response or None
        """
        key = self._generate_key(url, method, params)
        
        with self._lock:
            # Try memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                
                if self._is_expired(entry):
                    del self._memory_cache[key]
                else:
                    entry['last_accessed'] = time.time()
                    return entry['response']
            
            # Try disk cache
            response = self._load_from_disk(key)
            if response:
                # Add to memory cache
                self._memory_cache[key] = {
                    'response': response,
                    'cached_at': time.time(),
                    'expires_at': time.time() + self.default_ttl,
                    'last_accessed': time.time()
                }
                return response
        
        return None
    
    def set(
        self,
        url: str,
        response: Any,
        method: str = 'GET',
        params: Optional[dict] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache response.
        
        Args:
            url: Request URL
            response: Response to cache
            method: HTTP method
            params: Request parameters
            ttl: Time-to-live in seconds
        """
        if ttl is None:
            ttl = self.default_ttl
        
        key = self._generate_key(url, method, params)
        now = time.time()
        
        entry = {
            'response': response,
            'cached_at': now,
            'expires_at': now + ttl,
            'last_accessed': now
        }
        
        with self._lock:
            self._memory_cache[key] = entry
            self._cleanup_memory_cache()
        
        # Save to disk if enabled
        self._save_to_disk(key, response, ttl)
    
    def delete(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[dict] = None
    ) -> None:
        """
        Delete cached response.
        
        Args:
            url: Request URL
            method: HTTP method
            params: Request parameters
        """
        key = self._generate_key(url, method, params)
        
        with self._lock:
            self._memory_cache.pop(key, None)
        
        # Delete from disk
        if self.disk_cache:
            cache_file = self._get_disk_cache_path(key)
            cache_file.unlink(missing_ok=True)
    
    def clear(self) -> None:
        """Clear all cached responses."""
        with self._lock:
            self._memory_cache.clear()
        
        # Clear disk cache
        if self.disk_cache and self.cache_dir:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink(missing_ok=True)
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            total_entries = len(self._memory_cache)
            
            now = time.time()
            expired_entries = sum(
                1 for entry in self._memory_cache.values()
                if now > entry['expires_at']
            )
            
            return {
                'total_entries': total_entries,
                'valid_entries': total_entries - expired_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'disk_cache_enabled': self.disk_cache,
                'cache_hit_rate': getattr(self, '_hit_rate', 0.0)
            }