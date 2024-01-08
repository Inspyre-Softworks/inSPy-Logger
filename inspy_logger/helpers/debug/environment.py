import argparse
import json
import platform
import sys
import pyperclip
from pyperclip import copy

from inspy_logger.version import parse_version

VALID_DATA_FORMATS = [
    'markdown',
    'json',
    'text'
]


def determine_execution_mode():
    """
    Determines the execution mode of the program.

    Returns:
        str:
            Either 'Script' or 'REPL' depending on the execution mode.
    """
    return "REPL" if len(sys.argv) == 1 else "Script"


def get_operating_system_info():
    """
    Gets the operating system information.

    Returns:
        dict:
            A dictionary containing the operating system information.
    """

    os_name = platform.system()

    if os_name.lower() == 'windows':
        from inspy_logger.helpers.debug.system.winx import get_win_version_info

        return get_win_version_info()

    return {
        'name': platform.system(),
        'version': platform.release()
    }



def is_valid_data_format(data_format):
    """
    Checks if the specified data format is valid.

    This function is case-insensitive and compares the specified data format against the `VALID_DATA_FORMATS` list.


    Note:
        Valid formats are as follows:
            - markdown
            - json
            - text

    Parameters:
        data_format (str):
            The format you'd like the data to be returned in.

    Returns:
        bool:
            Whether the specified data format is valid.

    """
    return data_format.lower() in VALID_DATA_FORMATS


def get_system_info(format_type='markdown'):
    """
    Gathers system information and formats it based on the specified format type.

    Parameters:
        format_type (str):
            The format type for the output. Options are 'markdown', 'json', 'text'.
            Default is 'markdown'.

            Note:
                Valid formats are 'markdown', 'json', and 'text'.

    Returns:
        str:
            A string containing the system information in the specified format.
    """

    if not is_valid_data_format(format_type):
        raise ValueError(f"Invalid format type: {format_type}. Must be one of {VALID_DATA_FORMATS}")

    # Gather system information
    os_name = platform.system()
    os_version = platform.release()

    os_version_full = platform.version()

    if os_name.lower() == 'windows' and os_version == '10':
        from inspy_logger.helpers.debug.system.winx import is_win_11

        if is_win_11(os_version_full):
            os_version = '11'

    os_version = f'{os_version} ({os_version_full})'



    python_version = platform.python_version()



    sys_info = {
        'os_name': platform.system(),
        'os_version': platform.release(),
        'python_version': platform.python_version(),
        'isl_version': parse_version(),
        'execution_mode': "REPL" if len(sys.argv) == 1 else "Script"
    }

    # Format the information
    if format_type == 'markdown':
        return f"""
💻 **System Info:**
 - 💾 **Operating System**:
     - [x] {os_name} {os_version}
 - 🐍 **Python Version**: {python_version}
 - 🌈 **InSPy-Logger Version**: {sys_info['isl_version']}
 - - [{sys_info['execution_mode'] == 'Script'}] Script
   - [{sys_info['execution_mode'] == 'REPL'}] REPL
        """.strip()
    elif format_type == 'json':
        return json.dumps({
            "System Info": {
                "Operating System": f"{os_name} {os_version}",
                "Python Version": python_version,
                "InSPy-Logger Version": sys_info['isl_version'],
                "Execution Mode": sys_info['execution_mode']
            }
        }, indent=4)
    else:  # plain text
        return f"""
System Info:
Operating System: {os_name} {os_version}
Python Version: {python_version}
InSPy-Logger Version: {sys_info['isl_version']}
Execution Mode: {sys_info['execution_mode']}
        """.strip()


def fetch_system_info(copy_to_clipboard=False, format_type='markdown', print_to_console=None):
    """
    Fetches system information and formats it based on the specified format type.

    Parameters:
        copy_to_clipboard (bool):
            Whether to copy the output to the clipboard. Default is False.

        format_type (str):
            The format type for the output. Options are 'markdown',
            'json', 'text'. Default is 'markdown'.

        print_to_console (bool):
               Whether to print the output to the console. Default is None.

               Note:
                   If this is None, it will default to True.

    Returns:
        str:
            A string containing the system information in the specified format.
    """
    info = get_system_info(format_type)
    if copy_to_clipboard:
        copy(info)

    if print_to_console is None:
        print_to_console = True
    if print_to_console:
        print(info)
    return info
