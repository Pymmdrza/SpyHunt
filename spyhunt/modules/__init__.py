from typing import Any
from ..core.engine import SpyHuntEngine
from .subdomain_enum import run_subdomain_enum
from .port_scan import run_port_scan
from .vuln_scan import run_vulnerability_scan


def register_builtin_modules(engine: SpyHuntEngine) -> None:
    """
    Register all built-in modules with the SpyHunt engine.

    This allows CLI commands to reference modules by logical name.
    """
    engine.register_module("subdomain_enum", run_subdomain_enum)
    engine.register_module("port_scan", run_port_scan)
    engine.register_module("vuln_scan", run_vulnerability_scan)
