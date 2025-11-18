"""Module registry helpers for SpyHunt.

This module exposes a helper that registers built-in scanning modules on a
provided engine instance. Each module implements a lightweight interface with a
`scan` method (sync) and may optionally implement `scan_async`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .subdomain import SubdomainEnumerationModule
from .portscan import PortScanModule
from .vuln import VulnerabilityModule

if TYPE_CHECKING:  # pragma: no cover
    from spyhunt.core.engine import SpyHuntEngine


def register_builtin_modules(engine: "SpyHuntEngine") -> None:
    """Register built-in modules on the provided engine instance."""

    engine.register_module("subdomain_enum", SubdomainEnumerationModule)
    engine.register_module("port_scan", PortScanModule)
    engine.register_module("vuln_scan", VulnerabilityModule)
