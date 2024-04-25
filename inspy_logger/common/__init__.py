"""
Defines the logging configuration and constants used within the inSPy-Logger project. It includes the mapping of log
levels, default settings, and the `InspyLogger` class which is a central part of the logging framework.

Constants:
    PROG_NAME (str):
        The program name, imported from the project's `__about__` module.

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

    - inspy_logger.__about__:
        Provides metadata like program name and version, which are used in logging for contextual information.

    - inspy_logger.common.dirs:
        Provides common directory paths used in the logger, including the default log file path.

Example Usage:
    # This example shows how to access and use the constants defined in this module
    >>> from inspy_logger.common.logging_config import DEFAULT_LOGGING_LEVEL, LEVEL_MAP
    >>> print(DEFAULT_LOGGING_LEVEL)
    DEBUG
    >>> print(LEVEL_MAP['error'])
    40

    # Example of how `InspyLogger` might be used in the future (assuming further implementation)
    >>> logger = InspyLogger()
    >>> logger.log(level='error', message='This is an error message')

"""

import logging
from pathlib import Path
from typing import Union



from inspy_logger.__about__ import __PROG__ as PROG_NAME
from inspy_logger.constants import LEVEL_MAP
from inspy_logger.helpers.debug.system.session import is_interactive
from inspy_logger.helpers.logging import (
    build_name_from_caller
)
from inspy_logger.helpers.decorators import validate_type

__all__ = [
    "PROG_NAME",
    "LEVEL_MAP",
    "LEVELS",
    "DEFAULT_LOGGING_LEVEL",
    "InspyLogger"
]


LEVELS = list(LEVEL_MAP.values())
"""The list of level names."""


DEFAULT_LOGGING_LEVEL = logging.INFO
"""The default logging level."""


class InspyLogger:

    def __init__(
            self,
            name: str,
            auto_set_up: bool = None,
            console_level: int = DEFAULT_LOGGING_LEVEL,
            file_level: int = logging.DEBUG,
            file_name: Union[str, Path] = None,
    ):
        self.__name = None


        self.name = name



    @property
    def interactive_session(self):
        return is_interactive()

    @property
    def name(self):
        return self.__name

    @name.setter
    @validate_type(str)
    def name(self, new):
        if self.name is None:
            self.__name = new

    def build_name_from_caller(self, name= None,**kwargs):
        return build_name_from_caller(parent=self, **kwargs)

    def get_child_names(self):
        return [child.logger.name for child in self.children]
