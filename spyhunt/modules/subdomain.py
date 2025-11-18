"""Subdomain enumeration module."""

from __future__ import annotations

import socket
from typing import Dict, List

from .base import BaseModule


class SubdomainEnumerationModule(BaseModule):
    """Performs lightweight subdomain enumeration using DNS lookups."""

    name = "subdomain_enum"

    DEFAULT_WORDS = (
        "www",
        "mail",
        "api",
        "dev",
        "stage",
        "beta",
        "test",
    )

    def scan(self, target: str, **params) -> Dict[str, List[str]]:
        wordlist = params.get("wordlist")
        if isinstance(wordlist, str):
            try:
                with open(wordlist, "r", encoding="utf-8") as handle:
                    candidates = [line.strip() for line in handle if line.strip()]
            except OSError:
                candidates = list(self.DEFAULT_WORDS)
        else:
            candidates = list(self.DEFAULT_WORDS)

        findings: List[Dict[str, str]] = []
        resolved_count = 0
        for word in candidates:
            hostname = f"{word}.{target}" if not word.startswith("*") else word.replace("*", target)
            try:
                address = socket.gethostbyname(hostname)
                findings.append({"hostname": hostname, "address": address})
                resolved_count += 1
            except socket.gaierror:
                continue

        return self._build_result(
            findings,
            target=target,
            total_candidates=len(candidates),
            resolved=resolved_count,
        )
