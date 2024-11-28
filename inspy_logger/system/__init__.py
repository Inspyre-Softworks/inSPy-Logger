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


__all__ = [
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
