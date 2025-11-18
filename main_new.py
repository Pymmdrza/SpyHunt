#!/usr/bin/env python3
"""
SpyHunt 4.0 - Professional Cybersecurity Reconnaissance Framework
Modern entry point with enterprise-grade architecture and performance optimization.
"""

import sys
import os
from pathlib import Path

# Add the spyhunt package to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from spyhunt.cli.main import main

if __name__ == "__main__":
    main()