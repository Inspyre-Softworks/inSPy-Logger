import logging
import re
from logging import Formatter
import inspect
from inspy_logger.common import PROG_NAME, LEVEL_MAP
from inspy_logger.__about__ import __PROG__

"""
This module contains utility functions and classes for handling logging and
performing certain string and number operations.
"""


class CustomFormatter(Formatter):
    """
    CustomFormatter extends the logging.Formatter class to provide a custom
    formatting behavior. Specifically, it replaces '<ipython-input-...>'
    patterns in record.pathname with 'iPython'.
    """

    def format(self, record):
        """
        Replaces <ipython-input-...> pattern in record.pathname with 'iPython'.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: The formatted record.
        """
        # Replace <ipython-input-...> pattern in record.pathname
        record.pathname = re.sub(
            r"<ipython-input-\d+-\w+>|<module>", "iPython", record.pathname
        )
        return super().format(record)


def clean_module_name(module_name):
    """
    Replaces <ipython-input-...> pattern in the given module name with 'iPython'.

    Args:
        module_name (str): The module name to clean.

    Returns:
        str: The cleaned module name.
    """
    return re.sub(r"<ipython-input-\d+-\w+>", "iPython", module_name)


def is_number(string, force_integer=False, rounding=None):
    """
    Checks if a given string can be converted to a number and optionally
    rounds or converts the result to an integer.

    Args:
        string (str): The string to check.
        force_integer (bool, optional): If True, the result will be converted to an integer.
        rounding (int, optional): The number of decimal places to round to.

    Returns:
        float|int|str: The converted number, or the original string if it cannot be converted.
    """
    num = None

    print(f"Received string {string}")

    if isinstance(string, (int, float)):
        print("Detected that received string is actually an integer or float...")
        num = string
        print(f'Num is now "{num}" after detecting that "string" is indeed a string.')
    elif isinstance(string, str):
        print("Detected that received string is indeed a string.")

        try:
            print("Attempting to convert the string to a float...")
            # Try to convert the string to a float.
            num = float(string)
            print(
                f"After conversion attempt from string to float, {num} is {type(num)}"
            )

            # If rounding is specified, round the number.
            if rounding is not None and isinstance(rounding, int) and rounding >= 0:
                print("Detected parameters to return the number rounded.")
                num = round(num, rounding)
                print(f"After rounding, the number is {num}")

        except ValueError as e:
            print(e)
            # If a ValueError is raised, the string is not a number.
            num = string

    if force_integer and not isinstance(num, str):
        print("Detecting that we were instructed to return an integer.")
        num = int(num)
        print(f"After converting the number to an integer it is now; {num}")

    print(f"Returning number which is {num}")
    return num


def translate_to_logging_level(level_str):
    """
    Translates a given string to a logging level.

    Args:
        level_str (str): The string to translate.

    Returns:
        int: The corresponding logging level, or None if the string does not correspond to a level.
    """
    if not isinstance(level_str, str):
        return level_str

    level_str = level_str.lower()

    # Return the ps_logging level if it exists, else return None
    return LEVEL_MAP.get(level_str)


def get_level_name(level: int) -> (str, None):
    """
    Gets the name of the logging level.

    Args:
        level (int):
            The logging level.

    Returns:
        str:
            The name of the logging level.

        None:
            If the logging level is not found.
    """
    return next(
        (
            level_name.upper()
            for level_name, level_value in LEVEL_MAP.items()
            if level_value == level
        ),
        None,
    )


# def find_variable_in_call_stack(var_name, default=None):
#     """
#     Searches for a variable in the namespaces of all modules in the call stack.
#
#     Args:
#         var_name (str): The name of the variable to find.
#         default: Default value to return if the variable is not found.
#
#     Returns:
#         The first occurrence of the variable found in the call stack or the default value.
#     """
#     frame = inspect.currentframe()
#
#     try:
#         # Traverse the stack in the order of calling
#         while frame:
#             module = inspect.getmodule(frame)
#             if module and hasattr(module, var_name):
#                 print('FOUND THE VARIABLE IN THE CALL STACK!')
#                 return getattr(module, var_name)
#
#             frame = frame.f_back
#
#         return default
#     finally:
#         del frame


def find_variable_in_call_stack(var_name, default=None):
    frame = inspect.currentframe()

    try:
        # Iterate through the call stack
        while frame:
            # Check both the local and global namespace of the frame
            caller_locals = frame.f_locals
            caller_globals = frame.f_globals

            if var_name in caller_locals:
                return caller_locals[var_name]
            elif var_name in caller_globals:
                return caller_globals[var_name]

            # Move to the next frame
            frame = frame.f_back

        # Return default if the variable is not found in any frame
        return default
    finally:
        # Ensure that the reference to the frame is deleted to prevent reference cycles
        del frame


def check_preemptive_level_set() -> (str, None):
    """
    Checks if the preemptive level has been set in the call stack.

    Returns:
        bool: True if the preemptive level has been set, False otherwise.
    """
    return find_variable_in_call_stack("INSPY_LOG_LEVEL", False)


def determine_client_prog_name() -> (str, None):
    """
    Determines the name of the program that is calling the logger.

    Returns:
        str:
            The name of the program that is calling the logger.

        None:
            If the name of the program that is calling the logger cannot be determined.
    """
    valid_vars = [
        'PROG',
        'PROG_NAME',
        'PROGRAM_NAME',
        'PROGRAM',
        'PROGNAME',
        '__PROG__'
    ]
    for var in valid_vars:
        if prog_name := find_variable_in_call_stack(var):
            if prog_name != __PROG__:
                return prog_name


def find_argument_parser():
    """
    Finds the argument parser in the call stack.

    Returns:
        ArgumentParser:
            The argument parser in the call stack.

        None:
            If the argument parser cannot be found in the call stack.
    """
    return find_variable_in_call_stack("ARGUMENT_PARSER", None)
