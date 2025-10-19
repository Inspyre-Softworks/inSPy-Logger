"""Utility helpers for runtime environment checks."""

import __main__
import sys


def check_if_interactive() -> bool:
    """Return ``True`` when running in an interactive interpreter."""
    if getattr(sys, "ps1", None):
        return True

    if getattr(sys.flags, "interactive", False):
        return True

    modules = sys.modules
    if "IPython" in modules or "ipykernel" in modules:
        return True

    if hasattr(__main__, "__file__"):
        return False

    try:
        stdin_isatty = sys.stdin.isatty()
        stdout_isatty = sys.stdout.isatty()
    except (AttributeError, ValueError):
        return False

    return stdin_isatty and stdout_isatty
