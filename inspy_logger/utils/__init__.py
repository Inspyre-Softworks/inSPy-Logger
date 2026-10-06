"""Utility helpers for runtime environment checks."""

import __main__
import sys


def check_if_interactive() -> bool:
    """Return whether Python is running in an interactive environment."""
    if getattr(sys, "ps1", None) or getattr(sys.flags, "interactive", False):
        return True

    if "IPython" in sys.modules or "ipykernel" in sys.modules:
        return True

    if hasattr(__main__, "__file__"):
        return False

    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False
