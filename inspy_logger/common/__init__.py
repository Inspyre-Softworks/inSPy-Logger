"""
Defines the logging configuration and constants used within the inSPy-Logger project. It includes the mapping of log
levels, default settings, and the `InspyLogger` class which is a central part of the logging framework.

Constants:
    PROG_NAME (str):
        The program name, imported from the project's :mod:`inspy_logger.__about__` module.

    PROG_VERSION (str):
        The program version, imported from the project's `__about__` module.

    LEVEL_MAP (dict):
        A dictionary mapping string representations of logging levels to their corresponding logging module constants.

    LEVELS (list):
        A list of available logging levels derived from `LEVEL_MAP`.

    DEFAULT_LOGGING_LEVEL (logging level):
        The default logging level used throughout the project.

    DEFAULT_LOG_FILE_PATH (path):
        The default path where log files are stored, defined in `inspy_logger.common.dirs`.

Classes:
    InspyLogger:
        A placeholder for the logging class used in the inSPy-Logger project.

Dependencies:
    - logging:
        Used to define the logging levels and to be used in the `InspyLogger` class for actual logging.

    - :mod:`inspy_logger.__about__`:
        Provides metadata like program name and version, which are used in logging for contextual information.

    - inspy_logger.common.dirs:
        Provides common directory paths used in the logger, including the default log file path.

"""
from abc import ABC, abstractmethod
import logging

from inspy_logger.__about__ import __PROG__ as PROG_NAME, __VERSION__ as PROG_VERSION
from inspy_logger.config.dirs import DEFAULT_LOG_FILE_PATH
from inspy_logger.constants import LEVEL_MAP

__all__ = [
        "PROG_NAME",
        "PROG_VERSION",
        "LEVEL_MAP",
        "LEVEL_NAMES",
        "LEVELS",
        "DEFAULT_LOGGING_LEVEL",
        "DEFAULT_LOG_FILE_PATH",
        "InspyLogger"
    ]


LEVELS = list(LEVEL_MAP.values())
"""The list of level names."""

LEVEL_NAMES = [level.upper() for level in LEVEL_MAP.keys()]
"""The list of level names in uppercase."""


DEFAULT_LOGGING_LEVEL = logging.INFO
"""The default logging level."""


class InspyLogger(ABC):

    @property
    @abstractmethod
    def children(self):
        pass

    @property
    @abstractmethod
    def console_level(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def file_level(self):
        pass

    @property
    @abstractmethod
    def file_path(self):
        pass

    @property
    @abstractmethod
    def time_started(self):
        pass

    @property
    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def debug(self, message):
        pass

    @abstractmethod
    def info(self, message):
        pass

    @abstractmethod
    def warning(self, message):
        pass

    @abstractmethod
    def error(self, message):
        pass
