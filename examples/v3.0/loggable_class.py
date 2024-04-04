"""

File: 
    examples/v3.0/loggable_class.py

Author: 
    Inspyre Softworks

Description:
    This file is used to test the Loggable class.
    
"""
INSPY_LOG_LEVEL = 'info'

from inspy_logger import InspyLogger, Loggable
from inspy_logger.helpers.decorators import method_logger

MOD_LOG_DEVICE = InspyLogger(name="LoggableClassExample", console_level=INSPY_LOG_LEVEL)

LOG = MOD_LOG_DEVICE.logger


class LoggedClass(Loggable):
    def __init__(self):
        super().__init__(MOD_LOG_DEVICE, console_level=INSPY_LOG_LEVEL)

        log = self.log_device.logger

        log.debug('This is a debug message from the init method of a Loggable class.')


    def test_meth(self):
        log = self.method_logger

        log.debug('This is a debug message from a class-method child logger')
        log.info('This is an info message from a class-method child logger')
