#!/usr/bin/env python3
"""
SpyHunt - A comprehensive network scanning and vulnerability assessment tool
"""

from setuptools import setup, find_packages
import os
import sys

# Read the long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Package metadata
setup(
    name="spyhunt",
    version="4.0.0",
    author="Mmdrza",
    author_email="",
    description="A comprehensive network scanning and vulnerability assessment tool designed for security professionals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pymmdrza/spyhunt",
    project_urls={
        "Bug Reports": "https://github.com/Pymmdrza/spyhunt/issues",
        "Source": "https://github.com/Pymmdrza/spyhunt",
        "Documentation": "https://github.com/Pymmdrza/spyhunt#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
    ],
    keywords=[
        "security", "vulnerability", "scanner", "penetration-testing", 
        "reconnaissance", "bug-bounty", "web-security", "network-security",
        "subdomain-enumeration", "vulnerability-scanner", "security-tools",
        "pentesting", "ethical-hacking", "infosec", "cybersecurity",
        "xxe", "ssrf", "ssti", "nosql-injection", "crlf", "xss", "sqli"
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "spyhunt=spyhunt.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "spyhunt": [
            "payloads/*.txt",
            "scripts/*.sh",
            "scripts/*.py",
            "tools/f5bigip_scanner.py",
            "tools/pathhunt.py",
            "tools/assetfinder",
            "tools/smuggler/*.py",
            "tools/smuggler/configs/*.py",
            "tools/smuggler/payloads/*",
            "tools/whatwaf/**/*.py",
            "tools/whatwaf/content/files/*.txt",
            "tools/whatwaf/content/files/*.lst",
            "LICENSE",
            "README.md",
        ],
    },
    zip_safe=False,
    platforms=["any"],
    license="MIT",
    maintainer="Mmdrza",
    maintainer_email="pymmdrza@gmail.com",
)

