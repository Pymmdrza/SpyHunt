"""
Rate limiting implementation for network requests.
"""

import time
import asyncio
from typing import Optional
from threading import Lock
from collections import deque

from ..core.logger import get_logger


class RateLimiter:
    """
    Thread-safe rate limiter with token bucket algorithm.
    Supports both sync and async operations.
    """
    
    def __init__(self, requests_per_second: float = 10, window_size: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_second: Maximum requests per second
            window_size: Time window for rate limiting in seconds
        """
        self.requests_per_second = requests_per_second
        self.window_size = window_size
        self.tokens = requests_per_second
        self.max_tokens = requests_per_second
        self.last_update = time.time()
        self.lock = Lock()
        self.request_times = deque()
        self.logger = get_logger("spyhunt.rate_limiter")
        
        # Async semaphore for async operations
        self._async_semaphore: Optional[asyncio.Semaphore] = None
    
    def _update_tokens(self) -> None:
        """Update token count based on time elapsed."""
        now = time.time()
        time_passed = now - self.last_update
        self.tokens = min(self.max_tokens, self.tokens + time_passed * self.requests_per_second)
        self.last_update = now
    
    def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens for request (synchronous).
        
        Args:
            tokens: Number of tokens to acquire
        """
        with self.lock:
            self._update_tokens()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                self.request_times.append(time.time())
                return
            
            # Need to wait
            wait_time = (tokens - self.tokens) / self.requests_per_second
            self.logger.debug(f"Rate limit hit, waiting {wait_time:.2f}s")
            
        # Wait outside the lock
        time.sleep(wait_time)
        
        # Try again
        with self.lock:
            self._update_tokens()
            self.tokens -= tokens
            self.request_times.append(time.time())
    
    async def acquire_async(self, tokens: int = 1) -> None:
        """
        Acquire tokens for request (asynchronous).
        
        Args:
            tokens: Number of tokens to acquire
        """
        # Create semaphore if needed
        if self._async_semaphore is None:
            self._async_semaphore = asyncio.Semaphore(int(self.requests_per_second))
        
        async with self._async_semaphore:
            with self.lock:
                self._update_tokens()
                
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    self.request_times.append(time.time())
                    return
                
                # Need to wait
                wait_time = (tokens - self.tokens) / self.requests_per_second
                self.logger.debug(f"Rate limit hit, waiting {wait_time:.2f}s")
            
            # Wait outside the lock
            await asyncio.sleep(wait_time)
            
            # Try again
            with self.lock:
                self._update_tokens()
                self.tokens -= tokens
                self.request_times.append(time.time())
    
    def get_current_rate(self) -> float:
        """Get current request rate."""
        now = time.time()
        cutoff_time = now - self.window_size
        
        # Remove old requests
        while self.request_times and self.request_times[0] < cutoff_time:
            self.request_times.popleft()
        
        return len(self.request_times) / self.window_size
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        return {
            'requests_per_second_limit': self.requests_per_second,
            'current_rate': self.get_current_rate(),
            'available_tokens': self.tokens,
            'window_size': self.window_size,
            'requests_in_window': len(self.request_times)
        }