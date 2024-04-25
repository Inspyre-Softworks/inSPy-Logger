"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/helpers/debug/system/session.py
 

Description:
    

"""
import sys

__all__ = [
    'is_interactive',
]


def is_interactive():
    """
    Determines if the current session is interactive.

    Returns:
        bool:
            A flag indicating whether the current session is interactive.
    """
    if hasattr(sys, 'ps1') and sys.ps1:
        return True
    elif sys.flags.interactive:
        return True

    return False
