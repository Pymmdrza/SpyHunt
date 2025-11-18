"""Shared abstractions for SpyHunt scanning modules."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ModuleResult:
    """Simple container representing scan output."""

    findings: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "findings": self.findings,
            "metadata": self.metadata,
        }


class BaseModule:
    """Base class with helpers for concrete modules."""

    name: str = "module"

    def scan(self, target: str, **params) -> Dict[str, Any]:
        raise NotImplementedError

    def _build_result(self, findings: List[Dict[str, Any]], **metadata: Any) -> Dict[str, Any]:
        """Return a serializable dictionary compatible with ScanResult."""

        payload = ModuleResult(
            findings=findings,
            metadata={
                **metadata,
                "module": self.name,
                "timestamp": time.time(),
            },
        )
        return payload.to_dict()
