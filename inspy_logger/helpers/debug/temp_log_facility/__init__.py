"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/helpers/debug/temp_log_facility/__init__.py
 

Description:
    

"""
import logging
from inspy_logger.constants import DEFAULT_LOG_FORMAT
from inspy_logger.helpers import CustomFormatter
from inspy_logger.helpers.descriptors import RestrictedSetter
from inspy_logger.helpers.decorators import validate_type
from inspy_logger.helpers.logging import (
    build_name_from_caller,
    find_child_by_name
)
from rich.logging import RichHandler
from rich.highlighter import RegexHighlighter
from rich import print as rprint
import re


class LogHighlighter(RegexHighlighter):
   base_style = 'log.'
   highlights = [
       r"\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b",
   ]


level_highlighter = LogHighlighter()


class TemporaryLogger:
    """
    A temporary logger that can be used for debugging purposes.
    """
    loggers = {}
    build_name_from_caller = build_name_from_caller
    find_child_by_name     = find_child_by_name

    DEFAULT_FORMAT = DEFAULT_LOG_FORMAT
    formatter = RestrictedSetter(
        name='formatter',
        initial=None,
        allowed_types=logging.Formatter,
        restrict_setter=True,
    )

    handler = RestrictedSetter(
        name='handler',
        initial=None,
        allowed_types=(logging.Handler, RichHandler),
        restrict_setter=True,
    )

    @classmethod
    def get_rich_handler(cls, stream=None):
        return RichHandler(
            show_level=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True
        )

    def __init__(self, name, level=logging.DEBUG, log_format=None, stream=None, use_rich=True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        self.__handler = None
        self.__formatter = None

        formatter = logging.Formatter(log_format or self.DEFAULT_FORMAT)

        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def set_level(self, level):

        self.logger.setLevel()

    def set_up_logger(self):
        self.set_up_handler()

    def set_up_default_handler(self):
        self.handler = logging.StreamHandler()

    def  set_up_rich_handler(self):
        self.handler = self.get_rich_handler()

    def set_up_handler(self):
        """
        Configures and attaches a handler to the logger.

        If the `use_rich` attribute is set to `True`, a `RichHandler` will be used. Otherwise, a `StreamHandler` will be
        used. This handler will then be configured and attached to the logger, matching the existing logic. If the
        handler has already been set, it will not be reconfigured.

        Returns:
            None

        """
        if self.use_rich:
            self.set_up_rich_handler()
        else:
            self.set_up_default_handler()

        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(self.level)

        self.logger.addHandler(self.handler)


    def log(self, message):
        """
        Log a message using the temporary logger.
        """
        self.logger.debug(message)

    @property
    def use_rich(self):
        return self._use_rich

    @use_rich.setter
    @validate_type(bool)
    def use_rich(self, new):
        if not self.handler:
            self.__use_rich = new
        else:
            raise AttributeError("Cannot change the handler after it has been set.")
