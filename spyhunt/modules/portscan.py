"""Port scanning module."""

from __future__ import annotations

import socket
from typing import Any, Dict, Iterable, List, Tuple

from .base import BaseModule


class PortScanModule(BaseModule):
    """Performs a TCP connect scan over requested ports."""

    name = "port_scan"

    def scan(self, target: str, **params) -> Dict[str, List[Dict[str, Any]]]:
        ports = list(self._parse_ports(params))
        timeout = float(params.get("timeout", 1.0))

        findings: List[Dict[str, Any]] = []
        for port in ports:
            status, banner = self._check_port(target, port, timeout)
            findings.append(
                {
                    "port": port,
                    "status": status,
                    "service": banner,
                }
            )

        open_ports = [item for item in findings if item["status"] == "open"]
        return self._build_result(
            findings,
            target=target,
            scanned=len(ports),
            open_count=len(open_ports),
        )

    def _parse_ports(self, params: Dict[str, str]) -> List[int]:
        explicit_ports = params.get("ports")
        if explicit_ports:
            parts = []
            for token in str(explicit_ports).split(","):
                token = token.strip()
                if "-" in token:
                    start, end = token.split("-", 1)
                    try:
                        parts.extend(range(int(start), int(end) + 1))
                    except ValueError:
                        continue
                else:
                    try:
                        parts.append(int(token))
                    except ValueError:
                        continue
            if parts:
                return parts

        top_ports = int(params.get("top_ports", 1000))
        return list(range(1, top_ports + 1))

    def _check_port(self, host: str, port: int, timeout: float) -> Tuple[str, str]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                try:
                    sock.sendall(b"\r\n")
                    banner = sock.recv(64).decode(errors="ignore").strip()
                except socket.error:
                    banner = ""
                return "open", banner or "unknown"
            return "closed", ""
        except socket.error:
            return "filtered", ""
        finally:
            sock.close()
