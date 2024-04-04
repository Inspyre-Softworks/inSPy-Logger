import inspect
import logging
import re
from logging import Formatter
from pathlib import Path

from inspy_logger.__about__ import __PROG__
from inspy_logger.constants import LEVEL_MAP, DEFAULT_LOGGING_LEVEL
from inspy_logger.helpers.decorators import validate_type
from inspy_logger.helpers.descriptors import RestrictedSetter

"""
This module contains utility functions and classes for handling logging and
performing certain string and number operations.
"""


__all__ = [
    "check_preemptive_level_set",
    "clean_module_name",
    "CustomFormatter",
    "determine_client_prog_name",
    "determine_start_block",
    "find_argument_parser",
    "find_valid_vars_in_call_stack",
    "find_variable_in_call_stack",
    "get_level_name",
    "is_number",
    "translate_to_logging_level",
    "VALID_DEV_NAME_VARS",
    "VALID_LOG_FILE_VARS",
    "VALID_PROG_NAME_VARS",
    'determine_log_file_path',
    'determine_log_filepath',
]


class ValidVars:
    VALID_MODES = ['all', 'strict']
    _mode = RestrictedSetter(
        'mode',
        allowed_types=str,
        allowed_values=VALID_MODES,
        initial='strict'
    )

    def __init__(self, general_vars, strict_vars, mode=None):
        self.mode = mode or 'strict'
        self.__general_vars = None
        self.__strict_vars = None

        self.general_vars = general_vars
        self.strict_vars = strict_vars

    @property
    def general_vars(self):
        return self.__general_vars

    @general_vars.setter
    @validate_type(str, list, tuple, preferred_type=tuple)
    def general_vars(self, new):
        self.__general_vars = new

    @property
    def strict_vars(self):
        return self.__strict_vars

    @strict_vars.setter
    @validate_type(str, list, tuple, preferred_type=tuple)
    def strict_vars(self, new):
        self.__strict_vars = new

    @property
    def valid_vars(self):
        if self.mode == 'all':
            return self.general_vars + self.strict_vars
        elif self.mode == 'strict':
            return self.strict_vars

    def __repr__(self):
        return f"{self.__class__.__name__}(mode={self.mode}, "\
               f"general_vars={self.general_vars}, strict_vars={self.strict_vars})"

    def __str__(self):
        return self.__rich__()

    def __rich__(self):
        from rich.table import Table
        from rich.console import Console

        table = Table(
            title=self.__class__.__name__,
            show_lines=True,
            header_style='bold cyan',
            row_styles=['bold', 'italic'],
            highlight=True

        )
        table.add_column("Attribute")
        table.add_column("Value")

        table.add_row("Mode", self.mode)
        table.add_row("General Vars", ', '.join(self.general_vars))
        table.add_row("Strict Vars", ', '.join(self.strict_vars))

        console = Console()
        console.print(table)


VALID_LOG_FILE_VARS = [
    'LOG_FILE',
    'LOG_FILE_PATH',
    'INSPY_LOG_FILE',
    'INSPY_LOG_PATH',
    'INSPY_LOG_FILEPATH',
    'INSPY_LOG_FILE_PATH',
    'INSPY_LOGGER_FILEPATH',
    'INSPY_LOGGER_PATH',
    'INSPY_LOGGER_FILE_PATH'
]


VALID_LOG_LEVEL_VARS = [
    'LOG_LEVEL',
    'LOGGING_LEVEL',
    'INSPY_LOG_LEVEL',
    'INSPY_LOGGING_LEVEL',
]


VALID_ARGS_VARS = [
    'ARGUMENT_PARSER',
    'ARGS_PARSER',
    'ARGS',
    'PARSED_ARGS',
]

VALID_PROG_NAME_VARS = [
    'PROG',
    'PROG_NAME',
    'PROGRAM_NAME',
    'PROGRAM',
    'PROGNAME',
    '__PROG__',
]

VALID_DEV_NAME_VARS = ValidVars(
    [
        'DEV_NAME',
        'DEVNAME',
        'DEVELOPER_NAME',
        'DEVELOPER',
        'DEV',
        'AUTHOR',
        'SOFTWARE_ORG'
    ],
    [
        'INSPY_LOG_DEV_NAME',
        'INSPY_DEV_NAME',
        'INSPY_LOG_AUTHOR',
        'INSPY_AUTHOR',
        'INSPY_SOFTWARE_ORG',
        'INSPY_LOG_SOFTWARE_ORG'
    ],
    mode='strict'
)

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


def determine_level(client_prog_name):
    """
    Determines the level at which to output logs to the console.

    Returns:
        int:
            The level at which to output logs to the console.
    """

    level = DEFAULT_LOGGING_LEVEL

    if _preemptive_set := check_preemptive_level_set():
        level = translate_to_logging_level(_preemptive_set)

    if client_prog_name:
        if arg_parser := find_argument_parser():
            from inspy_logger.helpers.command_line import add_argument
            add_argument(arg_parser, level)
            args = arg_parser.parse_args()

            level = translate_to_logging_level(args.log_level)

    return level


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

    #print(f"Received string {string}")

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


def find_variable_in_call_stack(var_name, ignore_inspy_logger: bool = False, default=None):
    """
    Searches for a variable in the namespaces of all modules in the call stack.

    Args:
        var_name (str): The name of the variable to find.
        ignore_inspy_logger (bool): Whether to ignore variables from the Inspy-Logger module.
        default: Default value to return if the variable is not found.

    Returns:
        The first occurrence of the variable found in the call stack or the default value.
    """
    frame = inspect.currentframe()

    try:
        while frame:
            caller_locals = frame.f_locals
            caller_globals = frame.f_globals
            caller_name = frame.f_back.f_code.co_name if frame.f_back else None

            for var_source in [caller_locals, caller_globals]:
                if var_name in var_source:
                    var_value = var_source[var_name]

                    # Get the module where the variable was defined
                    var_module = inspect.getmodule(frame)

                    if ignore_inspy_logger and (var_module and 'inspy_logger' in var_module.__name__):
                        continue
                    return var_value

            frame = frame.f_back  # Move to the previous frame after checking both namespaces
        return default  # Variable not found in the call stack
    finally:
        del frame


def iterate_valid_vars(valid_vars, mode='strict'):
    """
    Iterates through the valid variables based on the mode.

    Args:
        valid_vars (list): The list of valid variables to iterate through.
        mode (str, optional): The mode to use. Defaults to 'strict'.

    Yields:
        str: The next valid variable.
    """
    if mode == 'all':
        yield from valid_vars
    elif mode == 'strict':
        for var in valid_vars:
            if var.startswith('INSPY'):
                yield var


def find_valid_vars_in_call_stack(valid_vars, mode='strict'):
    """
    Finds the first valid variable in the call stack.

    Parameters:
        valid_vars (list):
            The list of valid variables to search for.

        mode (str, optional):
            The mode to use. Defaults to 'strict'.

    Returns:
        str: The first valid variable found in the call stack.
    """
    for var in iterate_valid_vars(valid_vars, mode):
        if var_value := find_variable_in_call_stack(var, ignore_inspy_logger=True):
            return var_value


def check_preemptive_level_set() -> (str, None):
    """
    Checks if the preemptive level has been set in the call stack. If not, it checks to see if an argument parser exists
    in the stack

    Returns:
        bool: True if the preemptive level has been set, False otherwise.
    """
    for var in VALID_LOG_LEVEL_VARS:
        if level := find_variable_in_call_stack(var):
            return level

    if arg_parser := find_argument_parser():
        if hasattr(arg_parser, 'parsed') and hasattr(arg_parser.parsed, 'log_level'):
            return arg_parser.parsed.log_level

    return None


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
        if prog_name := find_variable_in_call_stack(var, ignore_inspy_logger=True):
            if prog_name != __PROG__:
                return prog_name


def determine_log_file_path() -> (Path, None):
    """
    Determines the path to the log file.

    This function first checks for the presence of environment variables that specify the path to the log file. If
    none are found, it then searches the call stack for variables that specify the path to the log file. If none are
    found, it then searches the call stack for an argument parser and uses the default log file path specified in the
    argument parser.

    Returns:
        str:
            The path to the log file.

        None:
            If the path to the log file cannot be determined.
    """

    for var in VALID_LOG_FILE_VARS:
        if log_file_path := find_variable_in_call_stack(var):
            return log_file_path

    if arg_parser := find_argument_parser():
        if hasattr(arg_parser, 'parsed') and hasattr(arg_parser.parsed, 'log_file'):
            return arg_parser.parsed.log_file

    return None


def determine_log_filepath() -> (Path, None):
    """
    Determines the path to the log file.

    Returns:
        str:
            The path to the log file.

        None:
            If the path to the log file cannot be determined.
    """
    return determine_log_file_path()


def determine_start_block() -> bool:
    """
    Determines if the logger should be blocked from starting.

    To set this, set the `BLOCK_LOGGER_START` variable in the calling module to `True` before importing Inspy-Logger.

    Returns:
        bool:
            True if the logger should be blocked from starting, False otherwise.

    """
    return find_variable_in_call_stack("BLOCK_LOGGER_START", False)


def find_argument_parser():
    """
    Finds the argument parser in the call stack.

    Returns:
        ArgumentParser:
            The argument parser in the call stack.

        None:
            If the argument parser cannot be found in the call stack.
    """
    for var in VALID_ARGS_VARS:
        if arg_parser := find_variable_in_call_stack(var):
            return arg_parser
