#!/usr/bin/env python3
"""
Setup script for SpyHunt 4.0 - Professional Cybersecurity Reconnaissance Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
README_PATH = Path(__file__).parent / "README.md"
if README_PATH.exists():
    with open(README_PATH, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Professional Cybersecurity Reconnaissance Framework"

# Read requirements
REQUIREMENTS_PATH = Path(__file__).parent / "requirements.txt"
if REQUIREMENTS_PATH.exists():
    with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = []

setup(
    name="spyhunt",
    version="4.0.0",
    author="c0deninja (Enhanced)",
    author_email="",
    description="Professional Cybersecurity Reconnaissance Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/spyhunt/spyhunt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.2.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.10.0",
            "flake8>=6.0.0",
            "mypy>=0.991",
            "pre-commit>=2.21.0",
        ],
        "security": [
            "bandit>=1.7.4",
            "safety>=2.3.0",
        ],
        "performance": [
            "uvloop>=0.17.0; sys_platform != 'win32'",
            "orjson>=3.8.0",
        ],
        "cloud": [
            "boto3>=1.26.0",
            "azure-identity>=1.12.0",
            "google-cloud-storage>=2.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "spyhunt=spyhunt.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "spyhunt": [
            "payloads/*.txt",
            "config/*.yaml",
            "data/*.json",
        ],
    },
    zip_safe=False,
    keywords="cybersecurity reconnaissance penetration-testing security-tools bug-bounty osint",
    project_urls={
        "Bug Reports": "https://github.com/spyhunt/spyhunt/issues",
        "Source": "https://github.com/spyhunt/spyhunt",
        "Documentation": "https://spyhunt.readthedocs.io/",
    },
)
