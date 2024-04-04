"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/system/linux.py
 

Description:
    

"""
import os


__all__ = [
    'get_user_name'
]


def get_user_name() -> str:
    """
    Get the current user's name.

    Returns:
        str:
            The user's name.

    """
    import pwd
    return pwd.getpwuid(os.getuid()).pw_gecos.split(',')[0]
