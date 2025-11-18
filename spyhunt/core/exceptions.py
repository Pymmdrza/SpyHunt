"""
Custom exceptions for SpyHunt framework.
Provides structured error handling with detailed context and recovery suggestions.
"""

from typing import Callable, Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    """Error codes for structured error handling."""
    # General errors
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # Network errors
    NETWORK_ERROR = "NETWORK_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    DNS_ERROR = "DNS_ERROR"
    SSL_ERROR = "SSL_ERROR"
    PROXY_ERROR = "PROXY_ERROR"
    
    # Authentication/Authorization errors
    AUTH_ERROR = "AUTH_ERROR"
    API_KEY_ERROR = "API_KEY_ERROR"
    PERMISSION_ERROR = "PERMISSION_ERROR"
    
    # Data/Parsing errors
    PARSE_ERROR = "PARSE_ERROR"
    JSON_ERROR = "JSON_ERROR"
    HTML_ERROR = "HTML_ERROR"
    ENCODING_ERROR = "ENCODING_ERROR"
    
    # Module/Plugin errors
    MODULE_ERROR = "MODULE_ERROR"
    PLUGIN_ERROR = "PLUGIN_ERROR"
    IMPORT_ERROR = "IMPORT_ERROR"
    
    # Resource errors
    FILE_ERROR = "FILE_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    DISK_ERROR = "DISK_ERROR"
    
    # Scanning errors
    SCAN_ERROR = "SCAN_ERROR"
    TARGET_ERROR = "TARGET_ERROR"
    PAYLOAD_ERROR = "PAYLOAD_ERROR"


class SpyHuntException(Exception):
    """
    Base exception class for SpyHunt framework.
    
    Provides structured error information including error codes,
    context data, and recovery suggestions.
    """
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        recovery_suggestion: Optional[str] = None
    ):
        """
        Initialize SpyHunt exception.
        
        Args:
            message: Human-readable error message
            error_code: Structured error code for programmatic handling
            context: Additional context information
            cause: Original exception that caused this error
            recovery_suggestion: Suggestion for recovering from this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause
        self.recovery_suggestion = recovery_suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error": self.error_code.value,
            "message": self.message,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "recovery_suggestion": self.recovery_suggestion,
            "exception_type": self.__class__.__name__
        }
    
    def __str__(self) -> str:
        """String representation of the exception."""
        return f"[{self.error_code.value}] {self.message}"


class ConfigurationError(SpyHuntException):
    """Raised when there's a configuration-related error."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if config_key:
            context['config_key'] = config_key
        if config_value is not None:
            context['config_value'] = config_value
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.CONFIGURATION_ERROR
        super().__init__(message, **kwargs)


class NetworkError(SpyHuntException):
    """Raised when there's a network-related error."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if url:
            context['url'] = url
        if status_code:
            context['status_code'] = status_code
        if response_time:
            context['response_time'] = response_time
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.NETWORK_ERROR
        super().__init__(message, **kwargs)


class ConnectionError(NetworkError):
    """Raised when there's a connection error."""
    
    def __init__(self, message: str, **kwargs):
        kwargs['error_code'] = ErrorCode.CONNECTION_ERROR
        kwargs['recovery_suggestion'] = "Check network connectivity and target availability"
        super().__init__(message, **kwargs)


class TimeoutError(NetworkError):
    """Raised when a network operation times out."""
    
    def __init__(self, message: str, timeout_value: Optional[float] = None, **kwargs):
        context = kwargs.get('context', {})
        if timeout_value:
            context['timeout_value'] = timeout_value
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.TIMEOUT_ERROR
        kwargs['recovery_suggestion'] = "Increase timeout value or check network conditions"
        super().__init__(message, **kwargs)


class RateLimitError(NetworkError):
    """Raised when rate limiting is triggered."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        requests_made: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if retry_after:
            context['retry_after'] = retry_after
        if requests_made:
            context['requests_made'] = requests_made
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.RATE_LIMIT_ERROR
        kwargs['recovery_suggestion'] = "Reduce request rate or implement backoff strategy"
        super().__init__(message, **kwargs)


class AuthenticationError(SpyHuntException):
    """Raised when there's an authentication error."""
    
    def __init__(
        self,
        message: str,
        auth_type: Optional[str] = None,
        endpoint: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if auth_type:
            context['auth_type'] = auth_type
        if endpoint:
            context['endpoint'] = endpoint
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.AUTH_ERROR
        kwargs['recovery_suggestion'] = "Check authentication credentials and permissions"
        super().__init__(message, **kwargs)


class APIKeyError(AuthenticationError):
    """Raised when there's an API key-related error."""
    
    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        context = kwargs.get('context', {})
        if service:
            context['service'] = service
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.API_KEY_ERROR
        kwargs['recovery_suggestion'] = "Verify API key validity and service availability"
        super().__init__(message, **kwargs)


class ParseError(SpyHuntException):
    """Raised when there's a parsing error."""
    
    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        data_source: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if data_type:
            context['data_type'] = data_type
        if data_source:
            context['data_source'] = data_source
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.PARSE_ERROR
        kwargs['recovery_suggestion'] = "Verify data format and encoding"
        super().__init__(message, **kwargs)


class ModuleError(SpyHuntException):
    """Raised when there's a module-related error."""
    
    def __init__(
        self,
        message: str,
        module_name: Optional[str] = None,
        module_version: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if module_name:
            context['module_name'] = module_name
        if module_version:
            context['module_version'] = module_version
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.MODULE_ERROR
        kwargs['recovery_suggestion'] = "Check module installation and dependencies"
        super().__init__(message, **kwargs)


class ScanError(SpyHuntException):
    """Raised when there's a scanning-related error."""
    
    def __init__(
        self,
        message: str,
        scan_type: Optional[str] = None,
        target: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if scan_type:
            context['scan_type'] = scan_type
        if target:
            context['target'] = target
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.SCAN_ERROR
        super().__init__(message, **kwargs)


class ValidationError(SpyHuntException):
    """Raised when there's a validation error."""
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if field_name:
            context['field_name'] = field_name
        if field_value is not None:
            context['field_value'] = field_value
        if expected_type:
            context['expected_type'] = expected_type
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.VALIDATION_ERROR
        kwargs['recovery_suggestion'] = "Check input format and constraints"
        super().__init__(message, **kwargs)


class ResourceError(SpyHuntException):
    """Raised when there's a resource-related error."""
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        resource_path: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get('context', {})
        if resource_type:
            context['resource_type'] = resource_type
        if resource_path:
            context['resource_path'] = resource_path
            
        kwargs['context'] = context
        super().__init__(message, **kwargs)


class FileError(ResourceError):
    """Raised when there's a file-related error."""
    
    def __init__(self, message: str, **kwargs):
        kwargs['error_code'] = ErrorCode.FILE_ERROR
        kwargs['recovery_suggestion'] = "Check file permissions and disk space"
        super().__init__(message, resource_type="file", **kwargs)


class MemoryError(ResourceError):
    """Raised when there's a memory-related error."""
    
    def __init__(self, message: str, memory_usage: Optional[int] = None, **kwargs):
        context = kwargs.get('context', {})
        if memory_usage:
            context['memory_usage'] = memory_usage
            
        kwargs['context'] = context
        kwargs['error_code'] = ErrorCode.MEMORY_ERROR
        kwargs['recovery_suggestion'] = "Reduce batch size or increase memory limits"
        super().__init__(message, resource_type="memory", **kwargs)


# Exception handler decorator
def handle_exceptions(default_return=None, reraise=True) -> Callable[..., Callable[..., Any | None]]:
    """
    Decorator for handling exceptions in a consistent way.
    
    Args:
        default_return: Default value to return on exception
        reraise: Whether to reraise SpyHunt exceptions
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SpyHuntException:
                if reraise:
                    raise
                return default_return
            except Exception as e:
                # Convert generic exceptions to SpyHunt exceptions
                spyhunt_exception = SpyHuntException(
                    message=f"Unexpected error in {func.__name__}: {str(e)}",
                    error_code=ErrorCode.UNKNOWN_ERROR,
                    cause=e
                )
                if reraise:
                    raise spyhunt_exception
                return default_return
        return wrapper
    return decorator