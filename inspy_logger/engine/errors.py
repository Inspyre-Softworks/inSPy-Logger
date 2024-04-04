"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/engine/errors.py
 

Description:
    

"""
from inspy_logger.errors import InSPyLoggerError


__all__ = [
    'InSPyLoggerEngineError',
]


class InSPyLoggerEngineError(InSPyLoggerError):
    pass


class InSPyLoggerEngineConfigError(InSPyLoggerEngineError):
    pass


class InSPyLoggerLogFileError(InSPyLoggerEngineError):
    message = "[Log File Error]\n" \
              "An error occurred while trying to access the log file."
    prefix = "Some further information from the caller:\n"

    def __init__(self, message=None, skip_print=False):
        self.__child_caller_frame = inspect.stack()[1]
        self.__child_caller_name = self.__child_caller_frame[3]

        self.message = f"[{self.__class__.__name__}] - {self.message}"

        message = f"{self.prefix} - {message}" if message is not None else ''

        self.message += message

        super(InSPyLoggerLogFileError, self).__init__(message=self.message, skip_print=skip_print)
