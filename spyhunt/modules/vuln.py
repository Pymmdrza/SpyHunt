"""Vulnerability scanning module."""

from __future__ import annotations

import random
from typing import Dict, List

from .base import BaseModule


class VulnerabilityModule(BaseModule):
    """Simulates lightweight vulnerability checks over targets."""

    name = "vuln_scan"

    CHECKS = (
        "xss",
        "sqli",
        "lfi",
        "rfi",
        "ssrf",
        "cors",
        "headers",
    )

    def scan(self, target: str, **params) -> Dict[str, List[Dict[str, str]]]:
        enabled_checks = [check for check in self.CHECKS if params.get(check) or params.get("all_checks")]
        if not enabled_checks:
            enabled_checks = list(self.CHECKS[:3])

        findings: List[Dict[str, str]] = []
        for check in enabled_checks:
            simulated_issue = random.random() < 0.2
            findings.append(
                {
                    "check": check,
                    "target": target,
                    "status": "vulnerable" if simulated_issue else "passed",
                    "severity": self._severity(simulated_issue),
                }
            )

        return self._build_result(
            findings,
            target=target,
            checks=len(enabled_checks),
        )

    def _severity(self, vulnerable: bool) -> str:
        if not vulnerable:
            return "none"
        return random.choice(["low", "medium", "high", "critical"])
