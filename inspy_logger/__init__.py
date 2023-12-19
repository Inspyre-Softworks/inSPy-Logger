#!/usr/bin/env python3
import inspect
import os
import logging
from rich.logging import RichHandler
from inspy_logger.__about__ import __prog__ as PROG_NAME
from inspy_logger.helpers import find_variable_in_call_stack

# Let's set up some constants.
LEVEL_MAP = [
    ('debug', logging.DEBUG),
    ('info', logging.INFO),
    ('warning', logging.WARNING),
    ('error', logging.ERROR),
    ('critical', logging.CRITICAL),
    ('fatal', logging.FATAL),
]
"""
List[Tuple[str, int]]:
    A list of tuples containing the name of a logging level and it's corresponding logging level constant.
"""

LEVELS = [level[0] for level in LEVEL_MAP]
"""The list of level names."""

DEFAULT_LOGGING_LEVEL = logging.DEBUG

logging_level = getattr

from inspy_logger.helpers import (
    translate_to_logging_level,
    clean_module_name,
    CustomFormatter,
)


class Logger:
    """
    A Singleton class responsible for managing the logging mechanisms of the application.
    """

    instances = {}  # A dictionary to hold instances of the Logger class.

    def __new__(cls, name, *args, **kwargs):
        """
        Creates or returns an existing instance of the Logger class for the provided name.

        Args:
            name (str): The name of the logger instance.

        Returns:
            Logger: An instance of the Logger class.
        """

        if name not in cls.instances:
            instance = super(Logger, cls).__new__(cls)
            cls.instances[name] = instance
            return instance
        return cls.instances[name]

    def __init__(
            self,
            name,
            console_level=DEFAULT_LOGGING_LEVEL,
            file_level=logging.DEBUG,
            filename="app.log",
            parent=None,
    ):
        """
        Initializes a logger instance.

        Args:
            name (str): The name of the logger instance.
            console_level (str, optional): The logging level for the console. Defaults to DEFAULT_LOGGING_LEVEL.
            file_level (str, optional): The logging level for the file. Defaults to logging.DEBUG.
            filename (str, optional): The name of the log file. Defaults to "app.log".
            parent (Logger, optional): The parent logger instance. Defaults to None.
        """

        if not hasattr(self, "logger"):
            self.__name = name
            self.logger = logging.getLogger(name)
            self.logger.setLevel(logging.DEBUG)
            determined_level = console_level

            if isinstance(console_level, str):
                determined_level = translate_to_logging_level(console_level)

            self.__console_level = determined_level
            self.filename = filename
            self.__file_level = file_level or DEFAULT_LOGGING_LEVEL
            self.parent = parent

            self.logger.debug("Initializing Logger")

            # Remove existing handlers
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            self.logger.propagate = False

            self.set_up_console()
            self.set_up_file()
            self.children = []

    @property
    def device(self):
        """
        Returns the logger instance.

        Returns:
            Logger: The logger instance.
        """
        return self.logger

    @property
    def name(self):
        """
        Returns the name of the logger instance.

        Returns:
            str: The name of the logger instance.
        """
        return self.logger.name

    def set_up_console(self):
        """
        Configures and attaches a console handler to the logger.
        """

        self.logger.debug("Setting up console handler")
        console_handler = RichHandler(
            show_level=True, markup=True, rich_tracebacks=True, tracebacks_show_locals=True
        )
        formatter = CustomFormatter(
            f"[{self.logger.name}] %(message)s"
        )
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.__console_level)
        self.logger.addHandler(console_handler)

    def set_up_file(self):
        """
        Configures and attaches a file handler to the logger.
        """

        self.logger.debug("Setting up file handler")
        file_handler = logging.FileHandler(self.filename)
        file_handler.setLevel(self.__file_level)
        formatter = CustomFormatter(
            "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s |-| %(filename)s:%(lineno)d"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def set_level(self, console_level=None, file_level=None):
        """
        Updates the logging levels for both console and file handlers.
        """

        self.logger.debug("Setting log levels")
        if console_level is not None:
            self.logger.handlers[0].setLevel(console_level)
            for child in self.children:
                child.set_level(console_level=console_level)

        if file_level is not None:
            self.logger.handlers[1].setLevel(file_level)
            for child in self.children:
                child.set_level(file_level=file_level)

    def get_child(self, name=None, console_level=None, file_level=None):
        console_level = console_level or self.__console_level
        caller_frame = inspect.stack()[1]

        if name is None:
            name = caller_frame.function

        caller_self = caller_frame.frame.f_locals.get("self", None)
        separator = ":" if caller_self and hasattr(caller_self, name) else "."
        child_logger_name = f"{self.logger.name}{separator}{name}"

        for child in self.children:
            if child.logger.name == child_logger_name:
                return child

        child_logger = Logger(name=child_logger_name, console_level=console_level, file_level=file_level, parent=self)
        self.children.append(child_logger)
        return child_logger

    def get_child_names(self):
        """
        Fetches the names of all child loggers associated with this logger instance.
        """

        self.logger.debug("Getting child logger names")
        return [child.logger.name for child in self.children]

    def get_parent(self):
        """
        Fetches the parent logger associated with this logger instance.
        """

        self.logger.debug("Getting parent logger")
        return self.parent

    def find_child_by_name(self, name: str, case_sensitive=True, exact_match=False):
        """
        Searches for a child logger by its name.

        Args:
            name (str): The name of the child logger to search for.
            case_sensitive (bool, optional): Whether the search should be case sensitive. Defaults to True.
            exact_match (bool, optional): Whether the search should only return exact matches. Defaults to False.

        Returns:
            list or Logger: If exact_match is True, returns the Logger instance if found, else returns an empty list.
                            If exact_match is False, returns a list of Logger instances whose names contain the search term.
        """
        self.logger.debug(f'Searching for child with name: {name}')
        results = []

        if not case_sensitive:
            name = name.lower()

        for logger in self.children:
            logger_name = logger.name if case_sensitive else logger.name.lower()
            if exact_match and name == logger_name:
                return logger
            elif not exact_match and name in logger_name:
                results.append(logger)

        return results

    def debug(self, message):
            """
            Logs a debug message.

            Args:
                message (str): The message to log.
            """
            self._log(logging.DEBUG, message, args=(), stacklevel=2)


    def info(self, message):
            """
            Logs an info message.

            Args:
                message (str): The message to log.
            """
            self._log(logging.INFO, message, args=(), stacklevel=2)


    def warning(self, message):
        """
        Logs a warning message.


        Args:
            message (str): The message to log.
        """
        self._log(logging.WARNING, message, args=(), stacklevel=2)

    def error(self, message):
        """
        Logs an error message.


        Args:
            message (str): The message to log.
        """
        self._log(logging.ERROR, message, args=(), stacklevel=2)

    def __repr__(self):
        name = self.name
        hex_id = hex(id(self))
        if self.parent is not None:
            parent_part = f' | Parent Logger: {self.parent.name} |'
            if self.children:
                parent_part += f' | Number of children: {len(self.children)} |'
        else:
            parent_part = f' | This is a root logger with {len(self.children)} children. '

        if parent_part.endswith('|'):
            parent_part = str(parent_part[:-2])

        return f'<Logger: {name} w/ level {self.logger.level} at {hex_id}{parent_part}>'


    @classmethod
    def create_logger_for_caller(cls):
        """
        Creates a logger for the module that calls this method.

        Returns:
            Logger: An instance of the Logger class for the calling module.
        """
        frame = inspect.currentframe().f_back
        if module_path := cls._determine_module_path(frame):
            return cls(module_path)
        else:
            raise ValueError("Unable to determine module path for logger creation.")

    @staticmethod
    def _determine_module_path(frame):
        """
        Determines the in-project path of the module from the call frame.

        Args:
            frame:
                The frame from which to determine the module path.

        Returns:
            str:
                The in-project path of the module.
        """
        if module := inspect.getmodule(frame):
            base_path = os.path.dirname(os.path.abspath(module.__file__))
            relative_path = os.path.relpath(frame.f_code.co_filename, base_path)
            return relative_path.replace(os.path.sep, '.').rstrip('.py')
        return None

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        """
        Low-level logging implementation, passing stacklevel to findCaller.
        """
        if self.logger.isEnabledFor(level):
            self.logger._log(level, msg, args, exc_info, extra, stack_info, stacklevel + 1)


found_level = find_variable_in_call_stack('INSPY_LOG_LEVEL', DEFAULT_LOGGING_LEVEL)

LOG_DEVICE = Logger(PROG_NAME, found_level)
MOD_LOG_DEVICE = LOG_DEVICE.get_child("log_engine", found_level)
MOD_LOGGER = MOD_LOG_DEVICE.logger
MOD_LOGGER.debug(f"Started logger for {__name__}.")

add_child = LOG_DEVICE.get_child

InspyLogger = Logger

from inspy_logger.helpers.base_classes import Loggable
