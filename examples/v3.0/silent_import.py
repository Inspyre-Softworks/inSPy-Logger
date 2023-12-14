"""

File: 
    examples/v3.0/silent_import.py

Author: 
    Inspyre Softworks

Description:
    This file is used to test the silent import feature of the logger.

"""
# Before we import the logger we set a variable in our namespace...
INSPY_LOG_LEVEL = 'info'

# Now we can import the logger...
from inspy_logger import InspyLogger, Loggable

# And we can use the logger as normal...
LOG_DEVICE = InspyLogger(name='example', console_level='info')

LOG = LOG_DEVICE.logger

# This will not show up
LOG.debug('This is a debug message.')


# This will show up
LOG.info('This is an info message.')

def test_func():
    logger = LOG_DEVICE.get_child(console_level='info')
    log = logger.logger
    log.debug('This is a debug message from a child logger')
    log.info('This is an info message from a child logger')


class LoggedClass(Loggable):
    def __init__(self):
        super().__init__(LOG_DEVICE)

    def test_meth(self):
        logger = self.log_device.get_child(console_level='info')
        log = logger.logger
        log.debug('This is a debug message from a class-method child logger')
        log.info('This is an info message from a class-method child logger')
