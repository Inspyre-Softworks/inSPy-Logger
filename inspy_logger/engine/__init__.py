import inspect
import os
import logging
import sys

from rich.logging import RichHandler

from inspy_logger.config import DEFAULT_LOG_FILE_PATH
from inspy_logger.engine.handlers import BufferingHandler
from inspy_logger.common import InspyLogger, DEFAULT_LOGGING_LEVEL
from inspy_logger.helpers import translate_to_logging_level, CustomFormatter, get_level_name, RestrictedSetter
from inspy_logger.helpers.decorators import add_aliases, method_alias, count_invocations, validate_type
from typing import List, Union, Optional
from pathlib import Path


@add_aliases
class Logger(InspyLogger):
    """
    A Singleton class responsible for managing the logging mechanisms of the application.
    """

    instances = {}  # A dictionary to hold instances of the Logger class.

    # Set the file path for the log file.
    file_path = RestrictedSetter('file_path', DEFAULT_LOG_FILE_PATH, allowed_types=(str, Path),preferred_type=Path)

    def __new__(cls, name, *args, **kwargs):
        """
        Creates or returns an existing instance of the Logger class for the provided name.

        Args:
            name (str): The name of the logger instance.

        Returns:
            Logger: An instance of the Logger class.
        """

        if name not in cls.instances:
            instance = super(Logger, cls).__new__(cls)
            cls.instances[name] = instance
            return instance
        return cls.instances[name]

    def __init__(
            self,
            name,
            auto_set_up=True,
            console_level=DEFAULT_LOGGING_LEVEL,
            file_level=logging.DEBUG,
            file_name="app.log",
            file_path=DEFAULT_LOG_FILE_PATH.parent,
            no_file_logging=False,
            parent=None,
    ):
        """
        Initializes a logger instance.

        Parameters:
            name (str):
                The name of the logger instance.

            auto_set_up (bool, optional):
                Whether to automatically set up the handlers for the logger. Defaults to True.

            console_level (str, optional):
                The logging level for the console. Defaults to DEFAULT_LOGGING_LEVEL.

            file_level (str, optional):
                The logging level for the file. Defaults to logging.DEBUG.

            file_name (str, optional):
                The name of the log file. Defaults to "app.log".

            no_file_logging (bool, optional):
                Whether to disable file logging. Defaults to False.

            parent (Logger, optional):
                The parent logger instance. Defaults to None.
        """
        # Check if the logger has already been initialized.
        if hasattr(self, 'logger'):
            return

        self.__call_counts = {}

        self.__console_level = translate_to_logging_level(console_level)
        self.__file_level = translate_to_logging_level(file_level)

        self.__children = []

        self.__name = name
        self.__no_file_logging = None
        self.__file_path = None

        self.logger = logging.getLogger(name)
        self.logger.debug('Debug message from logger')
        self.logger.setLevel(translate_to_logging_level(console_level))

        self.logger.propagate = False
        self.logger.start = self.start

        if 'inSPy-Logger' in self.logger.name:
            self.buffering_handler = BufferingHandler()
            self.logger.addHandler(self.buffering_handler)
            self.logger.debug('Initializing logger with buffering handler.')
        else:
            self.logger.debug('Initializing  logger without buffering handler.')

        self.no_file_logging = no_file_logging

        self.set_file_path = Path(file_path).expanduser().absolute().joinpath(file_name)

        self.parent = parent

        if not getattr(self, 'buffering_handler', None):
            self.set_up_handlers()

    @property
    def call_counts(self):
        """
        Property to get the call counts of decorated methods.

        Returns:
            dict:
                A dictionary containing the call counts of decorated methods.

        """
        return self.__call_counts

    @property
    def child_names(self):
        return self.get_child_names()

    @property
    def children(self):
        return self.__children

    @children.deleter
    def children(self):
        self.__children = []

    @property
    def console_level(self):
        """
        Returns the logging level for the console.

        Returns:
            int:
                The logging level for the console.
        """
        return self.__console_level

    @console_level.setter
    def console_level(self, level):
        """
        Sets the logging level for the console.

        Args:
            level:
                The logging level for the console.

        Returns:

        """
        self.set_level(console_level=translate_to_logging_level(level))

    @property
    def console_level_name(self):
        return get_level_name(self.console_level)

    @property
    def device(self):
        """
        Returns the logger instance.

        Returns:
            Logger:
                The logger instance.
        """
        logger = self
        logger.start = self.start.__get__(logger)
        return logger

    @property
    def file_level(self):
        """
        Returns the logging level for the file.

        Returns:
            int:
                The logging level for the file.
        """
        return self.__file_level

    @file_level.setter
    def file_level(self, level):
        """
        Sets the logging level for the file.

        Args:
            level: The logging level for the file.

        Returns:
            None
        """
        self.set_level(file_level=translate_to_logging_level(level))

    @property
    def file_level_name(self):
        return get_level_name(self.file_level)

    #@property
    #def file_path(self):
    #    return self.__file_path

    # @file_path.setter
    # @validate_type(str, Path, preferred_type=Path)
    # def file_path(self, new: Union[str, Path]) -> None:
    #     """
    #     Sets file-path for the log-file.
    #
    #     Args:
    #         new (str, Path):
    #             The new file-path for the log-file.
    #
    #     Returns:
    #
    #     """
    #     print('I was called')
    #
    #     if not self.no_file_logging:
    #         old = self.__file_path
    #
    #         self.__file_path = Path(new)
    #
    #         # We need to ensure that the
    #         try:
    #             new_path = Path(new)
    #             self.ensure_log_file_path()
    #         except Exception as e:
    #             self.__file_path = old
    #             raise e

    @property
    def name(self):
        """
        Returns the name of the logger instance.

        Returns:
            str:
                The name of the logger instance.
        """
        return self.logger.name

    @property
    def no_file_logging(self):
        return self.__no_file_logging

    @no_file_logging.setter
    @validate_type(bool)
    def no_file_logging(self, new):
        self.__no_file_logging = new

    def __build_name_from_caller(self, caller: inspect.FrameInfo, name: str = None):
        """
        Builds a name for a child logger from the caller's frame.

        Parameters:
            caller (inspect.FrameInfo):
                The frame of the caller.

        Returns:
            str:
                The name of the child-logger.

        """
        if name is None:
            name = caller.function

        caller_self = caller.frame.f_locals.get("self", None)
        separator = ":" if caller_self and hasattr(caller_self, name) else "."
        return f"{self.logger.name}{separator}{name}"

    def ensure_log_file_path(self):
        """
        Ensures that the log file path exists.
        """
        if not self.no_file_logging and not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)

            self.file_path.touch()

    def get_file_handler(self):
        """
        Fetches the file-handler for the logger.

        Returns:
            logging.FileHandler:
                The file handler for the logger.
        """
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):

                return handler

    @validate_type(str, Path, preferred_type=Path)
    def set_file_path(self, file_path):
        """
        Sets the file path for the logger.

        Args:
            file_path (str):
                The path to the log file.
        """
        try:
            old = self.file_path
            self.file_path = file_path
            self.ensure_log_file_path()
        except Exception as e:
            self.file_path = old
            raise



    def set_up_console(self):
        """
        Configures and attaches a console handler to the logger.
        """

        self.logger.debug("Setting up console handler")
        console_handler = RichHandler(
            show_level=True, markup=True, rich_tracebacks=True, tracebacks_show_locals=True
        )
        formatter = CustomFormatter(
            f"[{self.logger.name}] %(message)s"
        )
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.__console_level)
        self.logger.addHandler(console_handler)

    def set_up_file(self):
        """
        Configures and attaches a file handler to the logger.
        """
        self.ensure_log_file_path()
        file_handler = logging.FileHandler(self.file_path)
        file_handler.setLevel(self.__file_level)
        formatter = CustomFormatter(
            "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s |-| %(file_name)s:%(lineno)d"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def set_level(self, console_level=None, file_level=None) -> None:
        """
        Updates the logging levels for both console and file handlers.

        Args:
            console_level:
                The logging level for the console.

            file_level:
                The logging level for the file.

        Returns:
            None
        """

        self.logger.debug("Setting log levels")

        # If we received a console level, update the console level.
        if console_level is not None:
            console_level = translate_to_logging_level(console_level)

            # Set the `console_level` property to the new value.
            self.__console_level = console_level

            # Iterate through the handlers to get the right one.
            for handler in self.logger.handlers:
                if isinstance(handler, RichHandler):
                    handler.setLevel(console_level)

        # If we received a file level, update the file level.
        if file_level is not None:
            file_level = translate_to_logging_level(file_level)

            # Set the `file_level` property to the new value.
            self.__file_level = file_level

            # Iterate through the handlers to get the right one.
            for handler in self.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.setLevel(file_level)

        # Set the logger level to the minimum of the console and file levels
        self.logger.setLevel(min(self.__console_level, self.__file_level))

        # Recursively update the levels of all child loggers.
        for child in self.children:
            child.set_level(console_level=console_level, file_level=file_level)

    @method_alias('add_child', 'add_child_logger', 'get_child_logger')
    def get_child(self, name=None, console_level=None, file_level=None) -> InspyLogger:
        """
        Retrieves a child logger with the specified name, console level, and file level.

        Args:
            name (str, optional):
                The name of the child logger. Defaults to None.

            console_level (int, optional):
                The console log level for the child logger. Defaults to None.

            file_level (int, optional):
                The file log level for the child logger. Defaults to None.

        Returns:
            InspyLogger:
                The child logger with the specified name, console level, and file level.
        """
        # Determine the console level and file level for the child logger.

        # If the console level is not provided, use the console level of the parent logger
        console_level = console_level or self.console_level

        # If the file level is not provided, use the file level of the parent logger
        file_level = file_level or self.file_level

        # Get the name of the calling function if no name is provided
        caller_frame = inspect.stack()[1]

        cl_name = self.__build_name_from_caller(caller_frame, name)

        cl_name

        found_child = self.find_child_by_name(cl_name, exact_match=True)

        if found_child:
            return found_child

        child_logger = Logger(name=cl_name, console_level=console_level, file_level=file_level, parent=self)

        self.children.append(child_logger)

        return child_logger

    @method_alias('get_children_names', 'get_child_loggers')
    def get_child_names(self) -> List:
        """
        Fetches the names of all child loggers associated with this logger instance.
        """

        self.logger.debug("Getting child logger names")
        return [child.logger.name for child in self.children]

    def get_parent(self) -> InspyLogger:
        """
        Fetches the parent logger associated with this logger instance.
        """

        self.logger.debug("Getting parent logger")
        return self.parent

    def find_child_by_name(self, name: str, case_sensitive=True, exact_match=False) -> (List, InspyLogger):
        """
        Searches for a child logger by its name.

        Args:
            name (str):
                The name of the child logger to search for.

            case_sensitive (bool, optional):
                Whether the search should be case-sensitive. Defaults to True.

            exact_match (bool, optional):
                Whether the search should only return exact matches. Defaults to False.

        Returns:
            list or Logger: If exact_match is True, returns the Logger instance if found, else returns an empty list.
                            If exact_match is False, returns a list of Logger instances whose names contain the
                            search term.
        """
        self.logger.debug(f'Searching for child with name: {name}')
        results = []

        if not case_sensitive:
            name = name.lower()

        for logger in self.children:
            logger_name = logger.name if case_sensitive else logger.name.lower()
            if exact_match and name == logger_name:
                return logger
            elif not exact_match and name in logger_name:
                results.append(logger)

        return results

    @count_invocations
    def debug(self, message):
        """
        Logs a debug message.

        Args:
          message (str): The message to log.
        """
        self._log(logging.DEBUG, message, args=(), stacklevel=2)

    @count_invocations
    def info(self, message):
        """
        Logs an info message.

        Args:
            message (str): The message to log.
        """
        self._log(logging.INFO, message, args=(), stacklevel=2)

    @count_invocations
    def warning(self, message):
        """
        Logs a warning message.


        Args:
            message (str): The message to log.
        """
        self._log(logging.WARNING, message, args=(), stacklevel=2)

    @count_invocations
    def error(self, message):
        """
        Logs an error message.


        Args:
            message (str): The message to log.
        """
        self._log(logging.ERROR, message, args=(), stacklevel=2)

    def __repr__(self):
        name = self.name
        hex_id = hex(id(self))
        if self.parent is not None:
            parent_part = f' | Parent Logger: {self.parent.name} |'
            if self.children:
                parent_part += f' | Number of children: {len(self.children)} |'
        else:
            parent_part = f' | This is a root logger with {len(self.children)} children. '

        if parent_part.endswith('|'):
            parent_part = str(parent_part[:-2])

        return f'<Logger: {name} w/ levels {self.console_level_name}, {self.file_level_name} at {hex_id}{parent_part}>'

    @classmethod
    def create_logger_for_caller(cls):
        """
        Creates a logger for the module that calls this method.

        Returns:
            Logger: An instance of the Logger class for the calling module.
        """
        if 'ipkernel' in sys.modules or 'IPython' in sys.modules:
            # We're running in an interactive environment, return a logger named 'interactive'
            print(cls.instances)
            if cls.instances.get('Interactive-Python'):
                level = cls.instances.get('inSPy-Logger')
            return cls('Interactive-Python')
        frame = inspect.currentframe().f_back
        if module_path := cls._determine_module_path(frame):
            return cls(module_path)
        raise ValueError("Unable to determine module path for logger creation.")

    def replay_and_setup_handlers(self):
        """
        Replays the buffered logs and sets up the handlers for the logger.
        """
        if self.buffering_handler:
            self.buffering_handler.replay_logs(self.logger)

            # Remove the buffer handler
            self.logger.removeHandler(self.buffering_handler)

        # Set up the handlers
        if not self.logger.handlers:
            self.set_up_handlers()

    def set_up_handlers(self) -> None:
        """
        Sets up the handlers for the logger.
        """
        self.set_up_console()
        self.set_up_file()

    def to_dict(self):
        """
        Converts the logger properties into a dictionary format.

        Returns:
            dict:
                A dictionary containing the logger properties.

        """
        return {
            'Name': self.name,
            'Console Level': self.console_level_name,
            'File Level': self.file_level_name,
            'Parent': self.parent.name if self.parent else 'None',
            'Children': {
                'Count': len(self.children),
                'Names': self.child_names,
                'Loggers': [child.to_dict() for child in self.children]
            },
            'Handlers': {
                'Count': len(self.logger.handlers),
                'Handlers': self.logger.handlers
            },
            'Call Counts': self.call_counts,
            'Buffering Handler': 'Yes' if getattr(self, 'buffering_handler', None) else 'No'
        }

    def start(self, *args, **kwargs):
        """
        Starts the logger.
        """
        self.logger.warning('InspyLogger.start() is deprecated.')
        if not self.logger.handlers:
            self.set_up_handlers()

        if hasattr(self, 'buffering_handler'):
            self.replay_and_setup_handlers()

        return self

    @staticmethod
    def _determine_module_path(frame):
        """
        Determines the in-project path of the module from the call frame.

        Args:
            frame:
                The frame from which to determine the module path.

        Returns:
            str:
                The in-project path of the module.
        """
        if module := inspect.getmodule(frame):
            base_path = os.path.dirname(os.path.abspath(module.__file__))
            relative_path = os.path.relpath(frame.f_code.co_filename, base_path)
            return relative_path.replace(os.path.sep, '.').rstrip('.py')
        return None

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        """
        Low-level logging implementation, passing stacklevel to findCaller.
        """
        if self.logger.isEnabledFor(level):
            self.logger._log(level, msg, args, exc_info, extra, stack_info, stacklevel + 1)

    def __rich__(self):
        # Create a rich table with logger properties
        from rich.table import Table
        from rich import box

        table = Table(title=f'[bold]Logger: {self.name}[/bold]', box=box.ASCII, padding=(0, 1, 0, 1))
        table.add_column('Property', justify='right', style='cyan', no_wrap=True)
        table.add_column('Value', justify='left', style='magenta', no_wrap=True)

        table.add_row('Name', self.name)
        table.add_row('Console Level', self.console_level_name)
        table.add_row('File Level', self.file_level_name)
        table.add_row('Parent', self.parent.name if self.parent else 'None')
        table.add_row('Children', str(len(self.children)))
        table.add_row('Handlers', str(len(self.logger.handlers)))

        call_counts_str = ', '.join(f'{method}: {count}' for method, count in self.call_counts.items())

        if call_counts_str:
            table.add_row('Call Counts', call_counts_str)
        else:
            table.add_row('Call Counts', 'No method calls recorded')

        if getattr(self, 'buffering_handler', None):
            table.add_row('Buffering Handler', 'Yes' if self.buffering_handler else 'No')

        return table
