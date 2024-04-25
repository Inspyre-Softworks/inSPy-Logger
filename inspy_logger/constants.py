"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/constants.py
 

Description:
    

"""


import logging

DEFAULT_LOGGING_LEVEL = logging.DEBUG

LEVEL_MAP = {
    'internal': 5,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'fatal': logging.FATAL,
}
"""A mapping of level names to their corresponding logging levels."""


LEVELS = [level.upper() for level in LEVEL_MAP]

INTERNAL = LEVEL_MAP['debug'] - 5

API_URL_BASE = 'https://pypi.org/pypi/'
API_SUFFIX = '/json'


INTERACTIVE_SESSION = __name__ != '__main__'
"""A flag to indicate whether the session is interactive."""

DEFAULT_LOG_FORMAT = "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s |-| %(file_name)s:%(lineno)d"
