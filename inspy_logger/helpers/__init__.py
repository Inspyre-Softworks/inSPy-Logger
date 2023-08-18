import logging
import re
from logging import Formatter

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
    level_str = level_str.upper()

    # Mapping of string to ps_logging levels
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "NOTSET": logging.NOTSET,
    }

    # Return the ps_logging level if it exists, else return None
    return level_mapping.get(level_str)
