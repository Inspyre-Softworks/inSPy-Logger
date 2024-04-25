"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/system/__init__.py
 

Description:
    

"""
import platform
import sys
from pathlib import Path


__all__ = [
    'get_executable_filepath',
    'get_local_package_path',
    'get_python_version',
    'get_user_name',
    'SYSTEM_OS',
]


def __determine_os() -> str:
    """
    Determine the operating system.

    Returns:
        str:
            The operating system.

    """
    return platform.system().lower()


SYSTEM_OS = __determine_os()


if SYSTEM_OS == 'windows':
    from inspy_logger.system.win32 import *
elif SYSTEM_OS == 'linux':
    from inspy_logger.system.linux import *
elif SYSTEM_OS == 'darwin':
    from inspy_logger.system.mac_os import *


def get_executable_filepath() -> str:
    """
    Get the path to the executable file.

    Returns:
        str:
            The path to the executable file.

    """
    return sys.executable


def get_local_package_path() -> Path:
    """
    Get the path to the local package.

    Returns:
        Path:
            The path to the local package.

    """
    return Path(__file__).parent


def get_python_version() -> str:
    """
    Get the Python version.

    Returns:
        str:
            The Python version.

    """
    return sys.version
