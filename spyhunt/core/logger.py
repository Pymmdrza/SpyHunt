"""
Advanced logging system for SpyHunt framework.
Provides structured logging with performance optimization and security considerations.
"""

import logging
import logging.handlers
import sys
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union
from datetime import datetime
from threading import RLock

from .config import get_config, LogLevel


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_data.update(getattr(record, 'extra_fields', {}))
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record."""
        if not hasattr(record, 'extra_fields'):
            setattr(record, 'extra_fields', {})
        
        extra_fields = getattr(record, 'extra_fields', {})
        extra_fields.update(self.context)
        setattr(record, 'extra_fields', extra_fields)
        return True


class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._start_times: Dict[str, float] = {}
        self._lock = RLock()
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        with self._lock:
            self._start_times[operation] = time.time()
    
    def end_timer(self, operation: str, **kwargs) -> float:
        """End timing an operation and log the duration."""
        with self._lock:
            start_time = self._start_times.pop(operation, None)
            if start_time is None:
                self.logger.warning(f"Timer for '{operation}' was not started")
                return 0.0
            
            duration = time.time() - start_time
            self.logger.info(
                f"Operation '{operation}' completed",
                extra={
                    'extra_fields': {
                        'operation': operation,
                        'duration_seconds': duration,
                        **kwargs
                    }
                }
            )
            return duration
    
    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """Log performance data directly."""
        self.logger.info(
            f"Performance: {operation}",
            extra={
                'extra_fields': {
                    'operation': operation,
                    'duration_seconds': duration,
                    'performance_log': True,
                    **kwargs
                }
            }
        )


class SecurityLogger:
    """Logger for security events."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_auth_attempt(self, success: bool, username: Optional[str] = None, source_ip: Optional[str] = None, **kwargs) -> None:
        """Log authentication attempt."""
        level = logging.INFO if success else logging.WARNING
        message = "Authentication successful" if success else "Authentication failed"
        
        self.logger.log(
            level,
            message,
            extra={
                'extra_fields': {
                    'security_event': 'authentication',
                    'success': success,
                    'username': username,
                    'source_ip': source_ip,
                    **kwargs
                }
            }
        )
    
    def log_suspicious_activity(self, activity: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log suspicious activity."""
        self.logger.warning(
            f"Suspicious activity detected: {activity}",
            extra={
                'extra_fields': {
                    'security_event': 'suspicious_activity',
                    'activity': activity,
                    'details': details or {},
                }
            }
        )
    
    def log_access_violation(self, resource: str, action: str, **kwargs) -> None:
        """Log access violation."""
        self.logger.error(
            f"Access violation: {action} on {resource}",
            extra={
                'extra_fields': {
                    'security_event': 'access_violation',
                    'resource': resource,
                    'action': action,
                    **kwargs
                }
            }
        )


class SpyHuntLogger:
    """Enhanced logger for SpyHunt framework."""
    
    def __init__(self, name: str):
        self.name = name
        self._logger = logging.getLogger(name)
        self.performance = PerformanceLogger(self._logger)
        self.security = SecurityLogger(self._logger)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with stack trace."""
        kwargs['exc_info'] = True
        self._log(logging.ERROR, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal logging method."""
        extra_fields = kwargs.pop('extra_fields', {})
        
        if extra_fields:
            extra = {'extra_fields': extra_fields}
            self._logger.log(level, message, extra=extra, **kwargs)
        else:
            self._logger.log(level, message, **kwargs)
    
    def set_context(self, **context) -> None:
        """Set context for this logger."""
        context_filter = ContextFilter(context)
        
        # Remove existing context filters
        self._logger.filters = [f for f in self._logger.filters if not isinstance(f, ContextFilter)]
        
        # Add new context filter
        self._logger.addFilter(context_filter)
    
    def clear_context(self) -> None:
        """Clear context for this logger."""
        self._logger.filters = [f for f in self._logger.filters if not isinstance(f, ContextFilter)]


# Global logger registry
_loggers: Dict[str, SpyHuntLogger] = {}
_lock = RLock()


def get_logger(name: str = "spyhunt") -> SpyHuntLogger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        SpyHuntLogger instance
    """
    with _lock:
        if name not in _loggers:
            _loggers[name] = SpyHuntLogger(name)
        return _loggers[name]


def setup_logging(
    log_level: Optional[Union[str, LogLevel]] = None,
    log_file: Optional[str] = None,
    json_format: bool = False,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console_output: bool = True
) -> None:
    """
    Setup logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Path to log file
        json_format: Whether to use JSON formatting
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup files to keep
        console_output: Whether to output to console
    """
    config = get_config()
    
    # Determine log level
    if log_level is None:
        log_level = config.get('app.log_level', LogLevel.INFO.value)
    
    if isinstance(log_level, str):
        numeric_level = getattr(logging, log_level.upper())
    elif isinstance(log_level, LogLevel):
        numeric_level = getattr(logging, log_level.value)
    else:
        numeric_level = log_level
    
    # Ensure we have a valid numeric level
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # Determine log file
    if log_file is None:
        log_file = config.get('app.log_file')
    
    # Create formatters
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Setup framework loggers
    framework_logger = get_logger("spyhunt")
    framework_logger.info("Logging system initialized", extra_fields={
        'log_level': logging.getLevelName(numeric_level),
        'log_file': log_file,
        'json_format': json_format
    })


def log_function_call(func):
    """Decorator to log function calls with timing."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.performance.start_timer(func.__name__)
        
        try:
            result = func(*args, **kwargs)
            logger.performance.end_timer(func.__name__, success=True)
            return result
        except Exception as e:
            logger.performance.end_timer(func.__name__, success=False, error=str(e))
            logger.exception(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper


def log_method_call(cls):
    """Class decorator to log all method calls."""
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(cls, attr_name, log_function_call(attr))
    return cls