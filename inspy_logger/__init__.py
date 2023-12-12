#!/usr/bin/env python3
import inspect
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

    instances = {}

    def __new__(cls, name, *args, **kwargs):
        """
        Creates or returns an existing instance of the Logger class for the provided name.
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
        return self.logger

    @property
    def name(self):
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
        self.logger.debug("Getting child logger")
        console_level = console_level or DEFAULT_LOGGING_LEVEL
        caller_frame = inspect.stack()[1]

        if name is None:
            name = caller_frame.function

        caller_self = caller_frame.frame.f_locals.get("self", None)
        separator = ":" if caller_self and hasattr(caller_self, name) else "."
        child_logger_name = f"{self.logger.name}{separator}{name}"

        for child in self.children:
            if child.logger.name == child_logger_name:
                return child

        child_logger = Logger(child_logger_name, console_level, file_level, parent=self)
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

        return f'<Logger: {name} at {hex_id}{parent_part}>'


found_level = find_variable_in_call_stack('INSPY_LOG_LEVEL', DEFAULT_LOGGING_LEVEL)


LOG_DEVICE = Logger(PROG_NAME, found_level)
MOD_LOG_DEVICE = LOG_DEVICE.get_child("log_engine", found_level)
MOD_LOGGER = MOD_LOG_DEVICE.logger
MOD_LOGGER.debug(f"Started logger for {__name__}.")

add_child = LOG_DEVICE.get_child

InspyLogger = Logger

def _get_parent_logging_device():
    """
    Determines the parent logging device by inspecting the caller's log_device or parent_log_device attribute.

    Returns:
        Logger: The parent logging device.
    """
    MOD_LOGGER.debug("Determining parent logging device")
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals

    if "logger" in caller_locals:
        return caller_locals["logger"]
    elif "parent_log_device" in caller_locals:
        return caller_locals["parent_log_device"]
    else:
        raise ValueError("Unable to determine the parent logging device.")


class Loggable:
    """
    A metaclass to enhance classes with logging capabilities. Classes that inherit from
    'Loggable' can instantly access a logger without manually setting it up. This logger
    is derived from a parent logger, ensuring consistent logging behavior and hierarchy.

    Attributes:
        - log_device: The logger device associated with the instance of the class.
    """

    def __init__(self, parent_log_device=None, **kwargs):
        self.parent_log_device = parent_log_device
        self.__log_name = self.__class__.__name__
        if self.parent_log_device is not None:
            self.__log_device = self.parent_log_device.get_child(
                self.__class__.__name__
            )
        else:
            self.__log_device = _get_parent_logging_device().get_child(
                self.__class__.__name__
            )

    @property
    def log_device(self):
        return self.__log_device

    @log_device.setter
    def log_device(self, new):
        if not isinstance(new, Logger):
            raise TypeError('log_device must be of type "Logger"')

        self.__log_device = new

    def create_child_logger(self, name=None, override=False):
        """
        Creates and returns a child logger of this object's logger.

        Parameters:
            name (str, optional): The name of the child logger.
                If not provided, the name of the calling function is used.
            override (bool, optional): A flag to override the membership check. Defaults to False.

        Returns:
            Logger: An instance of the Logger class that represents the child logger.
        """
        if not override:
            self.__is_member__()

        if name is None:
            name = inspect.stack()[1][
                3
            ]  # Get the name of the calling function if no name is provided

        return self.log_device.get_child(name)

    def __is_member__(self):
        """
        Checks whether the caller of this method is a member of the same class.

        Raises:
            PermissionError: If the caller of this method is not a member of the same class.
        """
        log_device = self.log_device.get_child("__is_member__")
        log = log_device.logger

        current_frame = inspect.currentframe()
        log.debug(f"Current frame: {current_frame}")

        caller_frame = current_frame.f_back
        log.debug(f"Caller frame: {caller_frame}")

        caller_self = caller_frame.f_locals.get("self", None)
        log.debug(f"Caller self: {caller_self}")

        log.debug("Checking if caller is a member of this class...")
        if not isinstance(caller_self, self.__class__):
            raise PermissionError(
                "Access denied.\n"
                f"Method can only be accessed by members of the same class. {caller_self.__class__.__name__} is not such a member"
            )

        log.debug(f"Access granted to {caller_self.__class__.__name__}")
