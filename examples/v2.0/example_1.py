    
#!/usr/bin/env python3

# Import inSPy-Logger's InspyLogger class
from inspy_logger import InspyLogger
from logging import getLogger


PROG_NAME = 'TestProg'


def a_function(an_arg):
    """
    
    A function that does nothing but start it's own child-logger and then 
    uses that logger to announce that it can log
    
    Arguments:
    
        an_arg (str): A string that the function will inject into a log line.
    
    """
    log_name = PROG_NAME + '.a_function'
    log = getLogger(log_name)
    debug = log.debug
    debug(f'Logger started for {log_name}!')
    log.info(f'The string you provided is: {an_arg}')
    
    
def start_root_logger():
    """
    
    For this example we will set our level to 'info'. That means that log messages
    ranked as 'debug' will be the only log messages that will not be output to STDOUT
    
    """
    
    # An 'InspyLogger' instance does not resolve to a usable logger, but we'll need the instantiated class
    logger = InspyLogger(PROG_NAME, 'info')
    
    # Then we can extract the actual log device from the instantiated 'logger'
    root_logger = logger.device
    
    # A prefix for our output strings.
    # D.R.Y. - Don't Repeat Yourself
    prefix = 'This is a message with level: '
    
    # Here we'll use the root logger to attempt to send a debug message to the console. If you don't see it
    # after runtime, don't worry; that's the behavior we are after. Remember; only messages of level 'info'
    # and higher will be output to the console if the log level is set to 'info'
    root_logger.debug(prefix + 'debug')
    
    # Now a message with level 'info'. This message should be visible at runtime.
    root_logger.info(prefix + 'info')
    
    # Now a message with level 'warning'. Again, this message should be visible at runtime.
    root_logger.info(prefix + 'warning')
    
    # Now here are some of different levels. You can't, however, set InSPy-Logger to define any of these levels
    # as the threshold. In other words, if using InSPy-Logger the logger can not be started with any of the 
    # following logging levels being passed to the 'level' argument (the keyword argument for the 
    # 'InspyLogger' class) and will therefore -ALWAYS- output log messages with these log levels.
    _log = root_logger
    _log.error(prefix + 'error')
    _log.exception(prefix + 'exception')
    _log.critical(prefix + 'critical')
    _log.fatal(prefix + 'fatal')
    
    
start_root_logger()
a_function('Some important string')
