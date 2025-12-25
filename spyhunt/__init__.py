"""
SpyHunt - A comprehensive network scanning and vulnerability assessment tool

SpyHunt v4.0 (Security Hardened) - A comprehensive network scanning and vulnerability 
assessment tool designed for security professionals and penetration testers. This tool 
performs comprehensive reconnaissance and vulnerability assessment on target networks 
and web applications, combining multiple scanning techniques with various external tools 
to provide extensive security intelligence.

Author: Pymmdrza
License: MIT
Version: 4.0.0
"""

__version__ = "4.0.3"
__author__ = "Pymmdrza"
__license__ = "MIT"
__url__ = "https://github.com/Pymmdrza/spyhunt"

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__url__",
]

# Package metadata
VERSION = __version__
AUTHOR = __author__
LICENSE = __license__
URL = __url__

# Display banner on import (optional)
def get_banner():
    """Returns the SpyHunt banner"""
    return """
███████╗██████╗ ██╗   ██╗██╗  ██╗██╗   ██╗███╗   ██╗████████╗
██╔════╝██╔══██╗╚██╗ ██╔╝██║  ██║██║   ██║████╗  ██║╚══██╔══╝
███████╗██████╔╝ ╚████╔╝ ███████║██║   ██║██╔██╗ ██║   ██║   
╚════██║██╔═══╝   ╚██╔╝  ██╔══██║██║   ██║██║╚██╗██║   ██║   
███████║██║        ██║   ██║  ██║╚██████╔╝██║ ╚████║   ██║   
╚══════╝╚═╝        ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
                                                    
    v4.0 - Security Hardened Edition
    Network Scanning & Vulnerability Assessment Tool
    Author: Pymmdrza
    """

def print_banner():
    """Prints the SpyHunt banner"""
    print(get_banner())

