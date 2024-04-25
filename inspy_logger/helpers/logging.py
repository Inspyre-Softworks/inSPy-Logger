"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/helpers/logging.py
 

Description:
    

"""
from typing import List
from inspy_logger.types import InspyLogger

from inspy_logger import initialized

import inspect

if initialized:
    from inspy_logger import Logger

def get_child(parent: InspyLogger, caller_frame: inspect.FrameInfo, name=None, console_level=None, file_level=None) -> InspyLogger:
    """
    Retrieves a child logger with the specified name, console level, and file level.

    Parameters:
        parent (InspyLogger):
            The parent logger. (Required)

        caller_frame (inspect.FrameInfo):
            The frame of the caller. (Required)

        name (str, optional):
            The name of the child logger. Defaults to None.

        console_level (int, optional):
            The console log level for the child logger. Defaults to None.

        file_level (int, optional):
            The file log level for the child logger. Defaults to None.

    Returns:
        InspyLogger:
            The child logger with the specified name, console level, and file level.

    Raises:
        TypeError:
            If the parent is not an instance of InspyLogger.
    """
    if not isinstance(parent, InspyLogger):
        raise TypeError(f"Expected an instance of InspyLogger, but received {type(parent)}.")

    if hasattr(parent, 'no_file_logging') and parent.no_file_logging:
        file_level = None
    else:
        file_level = file_level or (parent.file_level)

    if not isinstance(caller_frame, inspect.FrameInfo):
        raise TypeError(f"'caller_frame' must be an instance of `inspect.FrameInfo`, but received `{type(caller_frame)}`.")

    # If the console level is not provided, use the console level of the parent logger
    console_level = console_level or parent.console_level

    cl_name = build_name_from_caller(parent, caller_frame, name)

    if found_child := find_child_by_name(cl_name, parent.children, exact_match=True):
        return found_child

    # Determine the console level and file level for the child logger.

    child_logger = Logger(name=cl_name, console_level=console_level, file_level=file_level, parent=parent)

    parent.children.append(child_logger)

    return child_logger


def find_child_by_name(name: str, children: List,case_sensitive=True, exact_match=False) -> (List, InspyLogger):
    """
    Searches for a child logger by its name.

    Args:
        name (str):
            The name of the child logger to search for.

        children (List):
            The list of child loggers to search through.

        case_sensitive (bool, optional):
            Whether the search should be case-sensitive. Defaults to True.

        exact_match (bool, optional):
            Whether the search should only return exact matches. Defaults to False.

    Returns:
        list or Logger: If exact_match is True, returns the Logger instance if found, else returns an empty list.
                        If exact_match is False, returns a list of Logger instances whose names contain the
                        search term.
    """
    results = []

    if not case_sensitive:
        name = name.lower()

    for logger in children:
        logger_name = logger.name if case_sensitive else logger.name.lower()
        if exact_match and name == logger_name:
            return logger
        elif not exact_match and name in logger_name:
            results.append(logger)


def build_name_from_caller(parent: InspyLogger, caller_frame: inspect.FrameInfo, name=None):
    """
    Builds a name for a child logger based on the caller's frame.

    Parameters:
        parent (InspyLogger):
            The parent logger. (Required)

        caller_frame (inspect.FrameInfo):
            The frame of the caller. (Required)

        name (str, optional):
            The name of the child logger. Defaults to None.

    Returns:
        str:
            The name for the child logger.
    """
    if name is None:
        name = caller_frame.function

    caller_self = caller_frame.frame.f_locals.get('self', None)

    separator = ":" if caller_self and hasattr(caller_self, name) else "."
    return f"{parent.logger.name}{separator}{name}"
