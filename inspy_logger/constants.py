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
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'fatal': logging.FATAL,
}
"""A mapping of level names to their corresponding logging levels."""
