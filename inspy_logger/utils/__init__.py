import sys
import __main__


import sys


def check_if_interactive():
    # Interactive environments won't have a standard script name
    if hasattr(sys, 'ps1') or not sys.stdin.isatty():
        return True  # Likely interactive (REPL or Jupyter)
    if hasattr(__main__, '__file__'):
        return False  # Running as a script
    return True
