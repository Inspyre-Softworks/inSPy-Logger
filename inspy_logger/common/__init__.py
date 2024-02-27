import logging

from inspy_logger.__about__ import __PROG__ as PROG_NAME, __VERSION__ as PROG_VERSION


__all__ = [
    "PROG_NAME",
    "PROG_VERSION",
    "LEVEL_MAP",
    "LEVELS",
    "DEFAULT_LOGGING_LEVEL",
    "InspyLogger"
]


LEVEL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'fatal': logging.FATAL,
}
"""A mapping of level names to their corresponding logging levels."""


LEVELS = list(LEVEL_MAP.values())
"""The list of level names."""


DEFAULT_LOGGING_LEVEL = logging.DEBUG
"""The default logging level."""


class InspyLogger:
    pass
