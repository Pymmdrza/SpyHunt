"""
Core configuration management for SpyHunt.
Provides centralized configuration with validation and environment support.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Log levels for the application."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(Enum):
    """Output format options."""
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
    CSV = "csv"
    XML = "xml"


@dataclass
class NetworkConfig:
    """Network-related configuration."""
    timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0
    max_concurrent_requests: int = 50
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    user_agent_rotation: bool = True
    verify_ssl: bool = False
    follow_redirects: bool = True
    max_redirects: int = 5


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    api_key_file: Optional[str] = None
    credential_store: Optional[str] = None
    enable_encryption: bool = True
    secure_headers: bool = True
    validate_certificates: bool = False
    sandbox_mode: bool = False


@dataclass
class PerformanceConfig:
    """Performance optimization configuration."""
    enable_caching: bool = True
    cache_ttl: int = 3600
    connection_pool_size: int = 100
    dns_cache_size: int = 1000
    memory_limit_mb: int = 2048
    cpu_cores: Optional[int] = None
    async_batch_size: int = 100


@dataclass
class OutputConfig:
    """Output configuration."""
    format: OutputFormat = OutputFormat.JSON
    pretty_print: bool = True
    include_metadata: bool = True
    save_raw_responses: bool = False
    compression: bool = False
    max_file_size_mb: int = 100


class Config:
    """
    Centralized configuration manager for SpyHunt.
    
    Supports multiple configuration sources with precedence:
    1. Environment variables
    2. Configuration files (YAML/JSON)
    3. Command line arguments
    4. Default values
    """
    
    def __init__(self, config_file: Optional[str] = None, **kwargs):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
            **kwargs: Additional configuration overrides
        """
        self.config_file = config_file
        self._config = self._load_default_config()
        
        # Load from file if provided
        if config_file:
            self._load_from_file(config_file)
        
        # Load from environment
        self._load_from_environment()
        
        # Apply overrides
        self._apply_overrides(kwargs)
        
        # Validate configuration
        self._validate()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            "app": {
                "name": "SpyHunt",
                "version": "4.0.0",
                "debug": False,
                "log_level": LogLevel.INFO.value,
                "log_file": None,
                "working_directory": str(Path.cwd()),
                "data_directory": str(Path.cwd() / "data"),
                "plugins_directory": str(Path.cwd() / "plugins"),
            },
            "network": asdict(NetworkConfig()),
            "security": asdict(SecurityConfig()),
            "performance": asdict(PerformanceConfig()),
            "output": asdict(OutputConfig()),
            "modules": {
                "enabled": [],
                "disabled": [],
                "auto_load": True,
            },
            "proxies": {
                "enabled": False,
                "http_proxy": None,
                "https_proxy": None,
                "proxy_list": None,
                "proxy_rotation": False,
            },
            "scanning": {
                "default_threads": 25,
                "max_threads": 100,
                "aggressive_mode": False,
                "stealth_mode": False,
                "custom_wordlists": {},
                "exclude_patterns": [],
            }
        }
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from file."""
        file_path = Path(config_file)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    file_config = yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    file_config = json.load(f) or {}
                else:
                    raise ValueError(f"Unsupported config file format: {file_path.suffix}")
            
            self._deep_merge(self._config, file_config)
            
        except Exception as e:
            raise ValueError(f"Error loading configuration file: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            "SPYHUNT_DEBUG": ("app", "debug", bool),
            "SPYHUNT_LOG_LEVEL": ("app", "log_level", str),
            "SPYHUNT_LOG_FILE": ("app", "log_file", str),
            "SPYHUNT_TIMEOUT": ("network", "timeout", int),
            "SPYHUNT_MAX_THREADS": ("scanning", "max_threads", int),
            "SPYHUNT_RATE_LIMIT": ("network", "rate_limit_requests", int),
            "SPYHUNT_USER_AGENT_ROTATION": ("network", "user_agent_rotation", bool),
            "SPYHUNT_VERIFY_SSL": ("network", "verify_ssl", bool),
            "SPYHUNT_ENABLE_CACHING": ("performance", "enable_caching", bool),
            "SPYHUNT_CACHE_TTL": ("performance", "cache_ttl", int),
            "SPYHUNT_MEMORY_LIMIT": ("performance", "memory_limit_mb", int),
            "SPYHUNT_OUTPUT_FORMAT": ("output", "format", str),
            "SPYHUNT_PRETTY_PRINT": ("output", "pretty_print", bool),
            "SPYHUNT_PROXY_HTTP": ("proxies", "http_proxy", str),
            "SPYHUNT_PROXY_HTTPS": ("proxies", "https_proxy", str),
            "SPYHUNT_STEALTH_MODE": ("scanning", "stealth_mode", bool),
            "SPYHUNT_AGGRESSIVE_MODE": ("scanning", "aggressive_mode", bool),
        }
        
        for env_var, (section, key, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if value_type == bool:
                        parsed_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        parsed_value = int(env_value)
                    elif value_type == float:
                        parsed_value = float(env_value)
                    else:
                        parsed_value = env_value
                    
                    if section not in self._config:
                        self._config[section] = {}
                    self._config[section][key] = parsed_value
                    
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid environment variable {env_var}={env_value}: {e}")
    
    def _apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """Apply configuration overrides."""
        self._deep_merge(self._config, overrides)
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _validate(self) -> None:
        """Validate configuration values."""
        # Validate network configuration
        if self._config["network"]["timeout"] <= 0:
            raise ValueError("Network timeout must be positive")
        
        if self._config["network"]["max_concurrent_requests"] <= 0:
            raise ValueError("Max concurrent requests must be positive")
        
        # Validate scanning configuration
        if self._config["scanning"]["max_threads"] <= 0:
            raise ValueError("Max threads must be positive")
        
        # Validate performance configuration
        if self._config["performance"]["memory_limit_mb"] <= 0:
            raise ValueError("Memory limit must be positive")
        
        # Validate directories
        for dir_key in ["working_directory", "data_directory"]:
            dir_path = Path(self._config["app"][dir_key])
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Cannot create directory {dir_path}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'network.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'network.timeout')
            value: Value to set
        """
        keys = key.split('.')
        target = self._config
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()
    
    def save(self, file_path: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save file (defaults to original config file)
        """
        if file_path is None:
            if self.config_file is None:
                raise ValueError("No file path specified and no original config file")
            file_path = self.config_file
        
        path_obj = Path(file_path)
        
        try:
            # Convert enums and other non-serializable objects to their values
            config_to_save = self._serialize_config(self._config.copy())
            
            with open(path_obj, 'w', encoding='utf-8') as f:
                if path_obj.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config_to_save, f, default_flow_style=False, indent=2)
                elif path_obj.suffix.lower() == '.json':
                    json.dump(config_to_save, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Unsupported file format: {path_obj.suffix}")
                    
        except Exception as e:
            raise ValueError(f"Error saving configuration: {e}")
    
    def _serialize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert non-serializable objects (like enums) to serializable values."""
        serialized = {}
        for key, value in config.items():
            if isinstance(value, dict):
                serialized[key] = self._serialize_config(value)
            elif isinstance(value, Enum):
                serialized[key] = value.value
            elif isinstance(value, (list, tuple)):
                serialized[key] = [
                    item.value if isinstance(item, Enum) else item
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized
    
    @property
    def network(self) -> NetworkConfig:
        """Get network configuration."""
        return NetworkConfig(**self._config["network"])
    
    @property
    def security(self) -> SecurityConfig:
        """Get security configuration."""
        return SecurityConfig(**self._config["security"])
    
    @property
    def performance(self) -> PerformanceConfig:
        """Get performance configuration."""
        return PerformanceConfig(**self._config["performance"])
    
    @property
    def output(self) -> OutputConfig:
        """Get output configuration."""
        output_dict = self._config["output"].copy()
        if isinstance(output_dict["format"], str):
            output_dict["format"] = OutputFormat(output_dict["format"])
        return OutputConfig(**output_dict)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style assignment."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in configuration."""
        return self.get(key) is not None


# Global configuration instance
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        _global_config = Config()
    return _global_config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config