"""
SpyHunt - Professional Cybersecurity Reconnaissance Framework
Author: Enhanced by Senior Python Developer

A comprehensive, high-performance cybersecurity reconnaissance tool 
built with enterprise-grade architecture and advanced optimization techniques.
"""

from .core.version import (
    SPYHUNT_VERSION,
    SPYHUNT_AUTHOR,
    SPYHUNT_NAME,
    SPYHUNT_TAGLINE,
)

__version__ = SPYHUNT_VERSION
__author__ = SPYHUNT_AUTHOR
__license__ = "MIT"

from .core.engine import SpyHuntEngine, ScanResult, ScanJob
from .core.config import Config
from .core.exceptions import SpyHuntException

__all__ = [
    "SpyHuntEngine",
    "ScanResult",
    "ScanJob",
    "Config",
    "SpyHuntException",
    "SPYHUNT_VERSION",
    "SPYHUNT_AUTHOR",
    "SPYHUNT_NAME",
    "SPYHUNT_TAGLINE",
]
