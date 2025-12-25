#!/usr/bin/env python3
"""
SpyHunt - Main Entry Point

This module serves as the entry point for the SpyHunt command-line tool.
When SpyHunt is installed via pip, running 'spyhunt' in the terminal
will execute the main() function defined here.
"""

import sys
import os

def main():
    """
    Main entry point for the SpyHunt CLI tool.
    
    This function is called when the user runs 'spyhunt' from the command line.
    It executes the main spyhunt.py script by running it as __main__.
    """
    try:
        # Get the path to spyhunt.py
        spyhunt_script = os.path.join(os.path.dirname(__file__), 'spyhunt.py')
        
        # Execute the script as if it were run directly
        # This ensures the 'if __name__ == "__main__"' block runs
        with open(spyhunt_script, 'r', encoding='utf-8') as f:
            code = compile(f.read(), spyhunt_script, 'exec')
            exec(code, {'__name__': '__main__', '__file__': spyhunt_script})
        
    except KeyboardInterrupt:
        print("\n\n[!] User interrupted the execution")
        sys.exit(0)
    except FileNotFoundError:
        print("[!] Error: spyhunt.py not found")
        print("[!] Please reinstall the package: pip install --upgrade --force-reinstall spyhunt")
        sys.exit(1)
    except ImportError as e:
        print(f"[!] Error importing SpyHunt modules: {e}")
        print("[!] Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

