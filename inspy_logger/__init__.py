#!/usr/bin/env python3
import contextlib
import sys
import inspect
import logging
from pypattyrn.behavioral.null import Null
from inspy_logger.common import PROG_NAME as ISL_PROG_NAME, DEFAULT_LOGGING_LEVEL, DEFAULT_LOG_FILE_PATH, LEVELS
from inspy_logger.helpers import find_variable_in_call_stack, check_preemptive_level_set, find_argument_parser, determine_start_block, determine_level

from inspy_logger.helpers import (
    translate_to_logging_level,
    clean_module_name,
    CustomFormatter,
    determine_client_prog_name,
    determine_log_file_path
)

# Existing log record factory
old_factory = logging.getLogRecordFactory()


def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    # Set the file_name attribute to the name of the file where the log is called
    frame = inspect.stack()[1]
    record.file_name = frame.filename
    return record


logging.setLogRecordFactory(record_factory)


from inspy_logger.engine import Logger

__all__ = [
    "clean_module_name",
    "CustomFormatter",
    "DEFAULT_LOGGING_LEVEL",
    "determine_level",
    "InspyLogger",
    "LOG_DEVICE",
    "Logger",
    "ISL_PROG_NAME",
    "translate_to_logging_level",
]

BLOCKED = determine_start_block()

LOG_FILE = determine_log_file_path()

LOG_DEVICE = None if BLOCKED else Logger(ISL_PROG_NAME)

MODULE_OBJ = sys.modules[__name__]

CLIENT_PROG_NAME = determine_client_prog_name()

INIT_LOG_LEVEL = determine_level(CLIENT_PROG_NAME)


def start_logger(override_block=True):
    """
    Starts the logger.

    Parameters:
        override_block (Union[bool, None], optional):
            A flag to override the block on the logger. Defaults to True.

    Note:
        You only need to run this function if you have blocked the logger from starting automatically.

    Returns:

    """
    global LOG_DEVICE
    global CLIENT_PROG_NAME
    global INIT_LOG_LEVEL

    if not BLOCKED or override_block:
        LOG_DEVICE = Logger(ISL_PROG_NAME)
        LOG_DEVICE.set_level(INIT_LOG_LEVEL)

        if CLIENT_PROG_NAME:

            prog_logger = Logger(
                CLIENT_PROG_NAME,
                LOG_DEVICE.console_level,
                LOG_DEVICE.file_level,
                file_name=DEFAULT_LOG_FILE_PATH.name,
                file_path=DEFAULT_LOG_FILE_PATH.parent
            )
            __all__.append('PROG_LOGGER')

        LOG_DEVICE.replay_and_setup_handlers()
    elif CLIENT_PROG_NAME:
        prog_logger = Null()

    with contextlib.suppress(NameError):
        global PROG_LOGGER

        PROG_LOGGER = prog_logger

        if isinstance(PROG_LOGGER, Null):
            from rich import print
            print("The logger has been blocked from starting. To start the logger, run `start_logger()`.")
        

InspyLogger = Logger


def _get_loggable():
    from inspy_logger.helpers.base_classes import Loggable
    import bisect
    # Add the `Loggable` class to `__all__` in alphabetical order.
    bisect.insort(__all__, 'Loggable')

    return Loggable


Loggable = _get_loggable()


start_logger(override_block=False)


deprecation_warning_deliveries = 0


def getLogger(*args, **kwargs):
    global deprecation_warning_deliveries

    if deprecation_warning_deliveries < 5:
        LOG_DEVICE.warning('The `getLogger` function is deprecated. Use `InspyLogger` instead.')
        deprecation_warning_deliveries += 1

    return InspyLogger(*args, **kwargs)
