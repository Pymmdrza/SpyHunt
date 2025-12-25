#!/usr/bin/env python3
"""
SpyHunt - Main Entry Point

This module serves as the entry point for the SpyHunt command-line tool.
When SpyHunt is installed via pip, running 'spyhunt' in the terminal
will execute the main() function defined here.
"""

import sys
import os

# Add the parent directory to the path to allow importing spyhunt module
# This is necessary when running as a package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Main entry point for the SpyHunt CLI tool.
    
    This function is called when the user runs 'spyhunt' from the command line.
    It imports and executes the main spyhunt.py script.
    """
    try:
        # Import the spyhunt module
        # The actual code execution happens when spyhunt.py is imported
        # since it contains the main logic at module level
        import spyhunt
        
    except KeyboardInterrupt:
        print("\n\n[!] User interrupted the execution")
        sys.exit(0)
    except ImportError as e:
        print(f"[!] Error importing SpyHunt modules: {e}")
        print("[!] Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

