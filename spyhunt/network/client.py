"""
High-performance HTTP client implementation with advanced features.
Provides both sync and async clients with connection pooling, caching, and rate limiting.
"""

import asyncio
import aiohttp
import requests
import time
import random
from typing import Dict, List, Optional, Any, Union, Callable
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass
from contextlib import asynccontextmanager
import ssl
import certifi

from ..core.config import get_config
from ..core.logger import get_logger
from ..core.exceptions import NetworkError, TimeoutError, RateLimitError, ConnectionError
from .rate_limiter import RateLimiter
from .cache import ResponseCache


@dataclass
class HTTPResponse:
    """HTTP response container."""
    url: str
    status_code: int
    headers: Dict[str, str]
    content: bytes
    text: str
    encoding: str
    response_time: float
    from_cache: bool = False
    
    @property
    def json(self) -> Any:
        """Parse response as JSON."""
        import json
        try:
            return json.loads(self.text)
        except json.JSONDecodeError as e:
            raise NetworkError(f"Invalid JSON response: {e}", url=self.url)
    
    def __bool__(self) -> bool:
        """Response is truthy if status code indicates success."""
        return 200 <= self.status_code < 400


class UserAgentRotator:
    """Rotate user agents for requests."""
    
    def __init__(self, user_agents: Optional[List[str]] = None):
        self.user_agents = user_agents or self._get_default_user_agents()
        self.current_index = 0
    
    def get_random(self) -> str:
        """Get random user agent."""
        return random.choice(self.user_agents)
    
    def get_next(self) -> str:
        """Get next user agent in rotation."""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent
    
    def _get_default_user_agents(self) -> List[str]:
        """Get default user agents."""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
        ]


class ProxyRotator:
    """Rotate proxies for requests."""
    
    def __init__(self, proxies: Optional[List[str]] = None):
        self.proxies = proxies or []
        self.working_proxies = self.proxies.copy()
        self.failed_proxies = []
        self.current_index = 0
    
    def get_next(self) -> Optional[Dict[str, str]]:
        """Get next working proxy."""
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        
        return {
            'http': proxy,
            'https': proxy
        }
    
    def mark_failed(self, proxy: str) -> None:
        """Mark proxy as failed."""
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            self.failed_proxies.append(proxy)
    
    def reset_failed(self) -> None:
        """Reset failed proxies for retry."""
        self.working_proxies.extend(self.failed_proxies)
        self.failed_proxies.clear()


class HTTPClient:
    """
    High-performance synchronous HTTP client.
    Features: connection pooling, retries, caching, rate limiting, proxy rotation.
    """
    
    def __init__(
        self,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        max_redirects: int = 5,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[ResponseCache] = None,
        user_agent_rotation: bool = True,
        proxy_list: Optional[List[str]] = None
    ):
        """Initialize HTTP client."""
        config = get_config()
        
        self.timeout = timeout or config.get('network.timeout', 10)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        
        # Rate limiting
        self.rate_limiter = rate_limiter or RateLimiter(
            requests_per_second=config.get('network.rate_limit_requests', 100),
            window_size=config.get('network.rate_limit_window', 60)
        )
        
        # Caching
        self.cache = cache or ResponseCache()
        
        # User agent rotation
        self.user_agent_rotation = user_agent_rotation
        if user_agent_rotation:
            self.user_agent_rotator = UserAgentRotator()
        
        # Proxy rotation
        self.proxy_rotator = ProxyRotator(proxy_list) if proxy_list else None
        
        # Session setup
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        # SSL context
        if verify_ssl:
            self.session.verify = certifi.where()
        
        # Connection pool settings
        from requests.adapters import HTTPAdapter
        adapter = HTTPAdapter(
            pool_connections=config.get('performance.connection_pool_size', 100),
            pool_maxsize=config.get('performance.connection_pool_size', 100),
            max_retries=0  # We handle retries ourselves
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.logger = get_logger("spyhunt.http_client")
    
    def _prepare_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Prepare request parameters."""
        # Headers
        headers = kwargs.get('headers', {})
        
        # User agent rotation
        if self.user_agent_rotation and 'User-Agent' not in headers:
            headers['User-Agent'] = self.user_agent_rotator.get_next()
        
        # Proxy rotation
        proxies = kwargs.get('proxies')
        if not proxies and self.proxy_rotator:
            proxies = self.proxy_rotator.get_next()
        
        # Request parameters
        params = {
            'method': method,
            'url': url,
            'headers': headers,
            'timeout': kwargs.get('timeout', self.timeout),
            'allow_redirects': self.follow_redirects,
            'stream': kwargs.get('stream', False),
            'verify': kwargs.get('verify', self.verify_ssl)
        }
        
        # Add optional parameters
        for key in ['data', 'json', 'params', 'files', 'auth', 'cookies']:
            if key in kwargs:
                params[key] = kwargs[key]
        
        if proxies:
            params['proxies'] = proxies
        
        return params
    
    def _make_request(self, **request_params) -> HTTPResponse:
        """Make HTTP request with error handling."""
        url = request_params['url']
        start_time = time.time()
        
        try:
            # Rate limiting
            self.rate_limiter.acquire()
            
            # Make request
            response = self.session.request(**request_params)
            response_time = time.time() - start_time
            
            # Create response object
            http_response = HTTPResponse(
                url=response.url,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                text=response.text,
                encoding=response.encoding or 'utf-8',
                response_time=response_time
            )
            
            # Log response
            self.logger.debug(f"HTTP {request_params['method']} {url}", extra_fields={
                'status_code': response.status_code,
                'response_time': response_time,
                'content_length': len(response.content)
            })
            
            return http_response
            
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Request timeout for {url}",
                url=url,
                timeout_value=request_params.get('timeout')
            )
        except requests.exceptions.ConnectionError as e:
            # Handle proxy failures
            proxies = request_params.get('proxies')
            if proxies and self.proxy_rotator:
                proxy_url = proxies.get('http') or proxies.get('https')
                if proxy_url:
                    self.proxy_rotator.mark_failed(proxy_url)
            
            raise ConnectionError(f"Connection error for {url}: {str(e)}", url=url)
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request error for {url}: {str(e)}", url=url)
    
    def request(
        self,
        method: str,
        url: str,
        use_cache: bool = True,
        **kwargs
    ) -> HTTPResponse:
        """
        Make HTTP request with retries and caching.
        
        Args:
            method: HTTP method
            url: Target URL
            use_cache: Whether to use cache
            **kwargs: Additional request parameters
            
        Returns:
            HTTPResponse object
        """
        # Check cache first
        if use_cache and method.upper() == 'GET':
            cached_response = self.cache.get(url)
            if cached_response:
                self.logger.debug(f"Cache hit for {url}")
                return cached_response
        
        # Prepare request
        request_params = self._prepare_request(method, url, **kwargs)
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._make_request(**request_params)
                
                # Cache successful GET responses
                if use_cache and method.upper() == 'GET' and response:
                    self.cache.set(url, response)
                
                return response
                
            except (NetworkError, ConnectionError, TimeoutError) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    self.logger.warning(f"Request failed, retrying {attempt + 1}/{self.max_retries}: {str(e)}")
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    
                    # Try next proxy if available
                    if self.proxy_rotator:
                        request_params['proxies'] = self.proxy_rotator.get_next()
                else:
                    self.logger.error(f"Request failed after {self.max_retries} retries: {str(e)}")
        
        # All retries failed
        if last_exception:
            raise last_exception
        
        raise NetworkError(f"Request failed for unknown reason: {url}", url=url)
    
    def get(self, url: str, **kwargs) -> HTTPResponse:
        """Make GET request."""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> HTTPResponse:
        """Make POST request."""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> HTTPResponse:
        """Make PUT request."""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> HTTPResponse:
        """Make DELETE request."""
        return self.request('DELETE', url, **kwargs)
    
    def head(self, url: str, **kwargs) -> HTTPResponse:
        """Make HEAD request."""
        return self.request('HEAD', url, **kwargs)
    
    def close(self) -> None:
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncHTTPClient:
    """
    High-performance asynchronous HTTP client.
    Features: connection pooling, retries, caching, rate limiting, proxy rotation.
    """
    
    def __init__(
        self,
        timeout: Optional[float] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verify_ssl: bool = True,
        follow_redirects: bool = True,
        max_redirects: int = 5,
        rate_limiter: Optional[RateLimiter] = None,
        cache: Optional[ResponseCache] = None,
        user_agent_rotation: bool = True,
        proxy_list: Optional[List[str]] = None,
        max_connections: int = 100,
        max_connections_per_host: int = 10
    ):
        """Initialize async HTTP client."""
        config = get_config()
        
        self.timeout = timeout or config.get('network.timeout', 10)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verify_ssl = verify_ssl
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.max_connections = max_connections
        self.max_connections_per_host = max_connections_per_host
        
        # Rate limiting
        self.rate_limiter = rate_limiter or RateLimiter(
            requests_per_second=config.get('network.rate_limit_requests', 100),
            window_size=config.get('network.rate_limit_window', 60)
        )
        
        # Caching
        self.cache = cache or ResponseCache()
        
        # User agent rotation
        self.user_agent_rotation = user_agent_rotation
        if user_agent_rotation:
            self.user_agent_rotator = UserAgentRotator()
        
        # Proxy rotation
        self.proxy_rotator = ProxyRotator(proxy_list) if proxy_list else None
        
        # Session (will be created in async context)
        self._session: Optional[aiohttp.ClientSession] = None
        
        self.logger = get_logger("spyhunt.async_http_client")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            # SSL context
            ssl_context = None
            if self.verify_ssl:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            # Connection limits
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=self.max_connections_per_host,
                ssl=ssl_context,
                enable_cleanup_closed=True
            )
            
            # Timeout settings
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                auto_decompress=True
            )
        
        return self._session
    
    def _prepare_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Prepare async request parameters."""
        # Headers
        headers = kwargs.get('headers', {})
        
        # User agent rotation
        if self.user_agent_rotation and 'User-Agent' not in headers:
            headers['User-Agent'] = self.user_agent_rotator.get_next()
        
        # Proxy
        proxy = kwargs.get('proxy')
        if not proxy and self.proxy_rotator:
            proxy_dict = self.proxy_rotator.get_next()
            if proxy_dict:
                proxy = proxy_dict.get('http') or proxy_dict.get('https')
        
        # Request parameters
        params = {
            'method': method,
            'url': url,
            'headers': headers,
            'allow_redirects': self.follow_redirects,
            'max_redirects': self.max_redirects,
            'ssl': self.verify_ssl
        }
        
        # Add optional parameters
        for key in ['data', 'json', 'params']:
            if key in kwargs:
                params[key] = kwargs[key]
        
        if proxy:
            params['proxy'] = proxy
        
        return params
    
    async def _make_request(self, **request_params) -> HTTPResponse:
        """Make async HTTP request with error handling."""
        url = request_params['url']
        start_time = time.time()
        
        try:
            # Rate limiting
            await self.rate_limiter.acquire_async()
            
            # Get session
            session = await self._get_session()
            
            # Make request
            async with session.request(**request_params) as response:
                content = await response.read()
                text = await response.text()
                response_time = time.time() - start_time
                
                # Create response object
                http_response = HTTPResponse(
                    url=str(response.url),
                    status_code=response.status,
                    headers=dict(response.headers),
                    content=content,
                    text=text,
                    encoding=response.charset or 'utf-8',
                    response_time=response_time
                )
                
                # Log response
                self.logger.debug(f"HTTP {request_params['method']} {url}", extra_fields={
                    'status_code': response.status,
                    'response_time': response_time,
                    'content_length': len(content)
                })
                
                return http_response
                
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Request timeout for {url}",
                url=url,
                timeout_value=self.timeout
            )
        except aiohttp.ClientConnectionError as e:
            # Handle proxy failures
            proxy = request_params.get('proxy')
            if proxy and self.proxy_rotator:
                self.proxy_rotator.mark_failed(proxy)
            
            raise ConnectionError(f"Connection error for {url}: {str(e)}", url=url)
        except aiohttp.ClientError as e:
            raise NetworkError(f"Request error for {url}: {str(e)}", url=url)
    
    async def request(
        self,
        method: str,
        url: str,
        use_cache: bool = True,
        **kwargs
    ) -> HTTPResponse:
        """
        Make async HTTP request with retries and caching.
        
        Args:
            method: HTTP method
            url: Target URL
            use_cache: Whether to use cache
            **kwargs: Additional request parameters
            
        Returns:
            HTTPResponse object
        """
        # Check cache first
        if use_cache and method.upper() == 'GET':
            cached_response = self.cache.get(url)
            if cached_response:
                self.logger.debug(f"Cache hit for {url}")
                return cached_response
        
        # Prepare request
        request_params = self._prepare_request(method, url, **kwargs)
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._make_request(**request_params)
                
                # Cache successful GET responses
                if use_cache and method.upper() == 'GET' and response:
                    self.cache.set(url, response)
                
                return response
                
            except (NetworkError, ConnectionError, TimeoutError) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    self.logger.warning(f"Request failed, retrying {attempt + 1}/{self.max_retries}: {str(e)}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    
                    # Try next proxy if available
                    if self.proxy_rotator:
                        proxy_dict = self.proxy_rotator.get_next()
                        if proxy_dict:
                            request_params['proxy'] = proxy_dict.get('http') or proxy_dict.get('https')
                else:
                    self.logger.error(f"Request failed after {self.max_retries} retries: {str(e)}")
        
        # All retries failed
        if last_exception:
            raise last_exception
        
        raise NetworkError(f"Request failed for unknown reason: {url}", url=url)
    
    async def get(self, url: str, **kwargs) -> HTTPResponse:
        """Make async GET request."""
        return await self.request('GET', url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> HTTPResponse:
        """Make async POST request."""
        return await self.request('POST', url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> HTTPResponse:
        """Make async PUT request."""
        return await self.request('PUT', url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> HTTPResponse:
        """Make async DELETE request."""
        return await self.request('DELETE', url, **kwargs)
    
    async def head(self, url: str, **kwargs) -> HTTPResponse:
        """Make async HEAD request."""
        return await self.request('HEAD', url, **kwargs)
    
    async def close(self) -> None:
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    @asynccontextmanager
    async def batch_requests(self, concurrency: int = 10):
        """Context manager for batch requests with concurrency control."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_request(method: str, url: str, **kwargs):
            async with semaphore:
                return await self.request(method, url, **kwargs)
        
        try:
            yield limited_request
        finally:
            pass