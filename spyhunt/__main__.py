#!/usr/bin/env python3
"""
SpyHunt - Main Entry Point

This module serves as the entry point for the SpyHunt command-line tool.
When SpyHunt is installed via pip, running 'spyhunt' in the terminal
will execute the main() function defined here.
"""

import sys
import os
import runpy

def main():
    """
    Main entry point for the SpyHunt CLI tool.
    
    This function is called when the user runs 'spyhunt' from the command line.
    It sets up the environment and runs the spyhunt.spyhunt module as __main__.
    """
    try:
        # Get the directory containing the spyhunt package
        package_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(package_dir)
        
        # Add parent directory to sys.path if not already there
        # This allows 'import spyhunt' to work properly
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Run the spyhunt.spyhunt module as if it were __main__
        # This executes all module-level code AND the if __name__ == "__main__" block
        runpy.run_module('spyhunt.spyhunt', run_name='__main__', alter_sys=True)
        
    except KeyboardInterrupt:
        print("\n\n[!] User interrupted the execution")
        sys.exit(0)
    except ImportError as e:
        print(f"[!] Error importing SpyHunt modules: {e}")
        print("[!] Please ensure all dependencies are installed:")
        print("    pip install -r requirements.txt")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except SystemExit:
        # Allow normal exit codes to pass through
        raise
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

