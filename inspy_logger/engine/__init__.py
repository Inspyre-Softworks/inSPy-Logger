import inspect
import os
import logging
import sys

from time import time

from rich.logging import RichHandler

from inspy_logger.config import DEFAULT_LOG_FILE_PATH
from inspy_logger.constants import LEVELS, INTERACTIVE_SESSION, INTERNAL, HANDLER_TYPES
from inspy_logger.engine.handlers import BufferingHandler
from inspy_logger.models.announcement import Announcement
from inspy_logger.common import InspyLogger, DEFAULT_LOGGING_LEVEL
from inspy_logger.helpers import (
    translate_to_logging_level, CustomFormatter, get_level_name,
    translate_to_logging_level_str
    )
from inspy_logger.helpers.decorators import add_aliases, method_alias, count_invocations, validate_type, \
    property_logging
from typing import List, Union, Optional
from pathlib import Path
from warnings import warn


@add_aliases
class Logger(InspyLogger):
    """
    A Singleton class responsible for managing the logging mechanisms of the application.
    """

    LEVELS = LEVELS
    INTERACTIVE_SESSION = INTERACTIVE_SESSION

    instances = {}  # A dictionary to hold instances of the Logger class.

    def __new__(cls, name, *args, **kwargs):
        """
        Creates or returns an existing instance of the Logger class for the provided name.

        Parameters:
            name (str):
                The name of the logger instance.

        Returns:
            Logger:
                An instance of the Logger class.
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
            init_announcement: Optional[Announcement] = None,
            init_announcement_template: str = None,
            announce_on_init: bool = True,
            announcement_level: Union[int, str] = 'debug'
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

            init_announcement (Announcement, optional):
                An announcement object to use for initialization. Defaults to None.

            init_announcement_template (str, optional):
                A template to use for the initialization announcement. Defaults to None.

                Note:
                    If both `init_announcement` and `init_announcement_template` are provided, `init_announcement` will
                    take precedence.

                    Built-In Placeholders:
                        - {name}: The name of the logger.
                        - {time_started}: The time the logger was started.
                        - {parent}: The name of the parent logger.


        """
        # Check if the logger has already been initialized.
        if hasattr(self, 'logger'):
            return

        self.__time_started = time()

        self.__announcement_made = False

        self.__call_counts = {}
        self.__console_level = translate_to_logging_level(console_level)
        self.__file_level = translate_to_logging_level(file_level)

        self.__children = []

        self.__name = name
        self.__no_file_logging = None
        self.__file_path = None
        self.__warnings_issued = set()

        self.logger = logging.getLogger(name)

        self.logger.setLevel(translate_to_logging_level(console_level))

        self.logger.propagate = False

        self.parent = parent

        self.logger.start = self.start

        if 'inSPy-Logger' in self.logger.name:
            self.buffering_handler = BufferingHandler()
            self.logger.addHandler(self.buffering_handler)
            self.internal('Initializing logger with buffering handler.')
        else:
            self.internal('Initializing  logger without buffering handler.')

        self.no_file_logging = no_file_logging

        self._file_path = Path(file_path).expanduser().absolute().joinpath(file_name)

        if not getattr(self, 'buffering_handler', None):
            self.set_up_handlers()

        self.__announcement = None

        if announce_on_init:

            if init_announcement and isinstance(init_announcement, Announcement):
                self.__announcement = init_announcement
            elif init_announcement_template:
                self.__announcement = Announcement(
                        self,
                        init_announcement_template,
                        announcement_level
                        )

            if self.__announcement is None:
                self.__announcement = Announcement(
                        self,
                        Announcement.DEFAULT_INITIALIZATION_ANNOUNCEMENT,
                        announcement_level
                        )

            if auto_set_up:
                self.announce_initialization()

    @property
    def announcement(self) -> Announcement:
        return self.__announcement

    @announcement.setter
    @validate_type(Announcement, str, preferred_type=Announcement)
    def announcement(self, new: Union[Announcement, str]) -> None:
        if not self.announcement_made and isinstance(new, Announcement):
            self.__announcement = new

    @property
    def announcement_level(self) -> int:
        if not self.announcement:
            return self.console_level
        return self.announcement.announcement_level

    @property
    def announcement_made(self) -> bool:
        return self.announcement.announced

    @property
    def call_counts(self) -> dict:
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
    def children(self) -> List[InspyLogger]:
        return self.__children

    @children.deleter
    def children(self):
        self.__children = []

    @property
    def console_level(self) -> int:
        """
        Returns the logging level for the console.

        Returns:
            int:
                The logging level for the console.
        """
        return self.__console_level

    @console_level.setter
    @validate_type(
            str, int,
            preferred_type=str,
            conversion_funcs={int: translate_to_logging_level_str}
            )
    def console_level(self, level):
        """
        Sets the logging level for the console.

        Parameters:
            level:
                The logging level for the console.

        Returns:

        """
        if level.upper() not in LEVELS:
            raise ValueError(f'Invalid logging level: {level}. Please provide a valid logging level; one of {LEVELS}')

        self.__console_level = translate_to_logging_level(level)

        self.__apply_level_change('console')

    @property
    def console_level_name(self):
        self.internal('Test message')
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
    def file_level(self) -> int:
        """
        Returns the logging level for the file.

        Returns:
            int:
                The logging level for the file.
        """
        return self.__file_level

    @file_level.setter
    @validate_type(
            str, int,
            preferred_type=str,
            conversion_funcs={int: translate_to_logging_level_str}
            )
    def file_level(self, level):
        """
        Sets the logging level for the file.

        Parameters:
            level: The logging level for the file.

        Returns:
            None
        """
        if level.upper() not in LEVELS:
            raise ValueError(f'Invalid logging level: {level}. Please provide a valid logging level; one of {LEVELS}')

        self.__file_level = translate_to_logging_level(level)

        self.__apply_level_change('file')

    @property
    def file_level_name(self) -> str:
        return get_level_name(self.file_level)

    @property
    def file_path(self) -> Path:
        """
        Returns the path to the log file.

        Returns:
            Path:
                The path to the log file.

        """
        return self._file_path

    @file_path.setter
    def file_path(self, new):
        self._file_path = new

    @property
    def interactive_session(self) -> bool:
        return hasattr(sys, 'ps1') and sys.ps1

    @property
    def isEnabledFor(self, level):
        return self.logger.isEnabledFor(level)

    @property
    def name(self) -> str:
        """
        Returns the name of the logger instance.

        Returns:
            str:
                The name of the logger instance.
        """
        return self.logger.name

    @property
    def no_file_logging(self) -> bool:
        return self.__no_file_logging

    @no_file_logging.setter
    @validate_type(bool)
    def no_file_logging(self, new):
        self.__no_file_logging = new

    @property
    def time_started(self) -> float:
        """
        Returns the time the logger was started.
        """
        return self.__time_started

    @property
    def warnings_issued(self) -> set:
        """
        Returns the one-time warnings issued by the logger.

        Since:
            v3.2.0

        Returns:
            set:
                A set containing the one-time warnings issued by the logger.
        """
        return self.__warnings_issued

    def __apply_level_change(self, handler_type):
        """
        Applies the level change to the specified handler type and the logger's children.

        Parameters:
            handler_type (str):
                The type of handler to apply the level change to.

        Returns:
            None

        Raises:
            ValueError:
                If the handler type is invalid.
        """
        handler_type = handler_type.lower()
        if handler_type not in HANDLER_TYPES:
            raise ValueError(
                    f'Invalid handler type: {handler_type}. '
                    f'Please provide a valid handler type; one of {HANDLER_TYPES}'
                    )

        level = getattr(self, f'{handler_type}_level')

        for handler in self.logger.handlers:
            if isinstance(handler, HANDLER_TYPES[handler_type]):
                handler.setLevel(level)

        self.logger.setLevel(translate_to_logging_level(level))

        for child in self.children:
            child.set_level(**{f'{handler_type}_level': level})

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

    def has_child(self, name):
        """
        Checks if the logger has a child with the specified name.

        Parameters:
            name (str):
                The name of the child logger.

        Returns:
            bool:
                True if the logger has a child with the specified name, else False.
        """

        return name in self.child_names

    @validate_type(str, Path, preferred_type=Path)
    def set_file_path(self, file_path):
        """
        Sets the file path for the logger.

        Parameters:
            file_path (str):
                The path to the log file.
        """
        old = self.file_path
        try:

            self.file_path = file_path
            self.ensure_log_file_path()
        except Exception:
            warn(f"Unable to set file path to {file_path}. Reverting to {old}")
            self.file_path = old
            raise

    def set_up_console(self):
        """
        Configures and attaches a console handler to the logger.
        """

        self.internal("Setting up console handler")
        console_handler = RichHandler(
                show_level=True, markup=True, rich_tracebacks=True,
                tracebacks_show_locals=True
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

    def set_level(self, console_level=None, file_level=None, override=False, call_from_setter=False) -> None:
        """
        Updates the logging levels for both console and file handlers.

        Parameters:
            console_level:
                The logging level for the console.

            file_level:
                The logging level for the file.

            override (bool):
                Whether to override the `no_file_logging` option. Defaults to `False`.

            call_from_setter (bool):
                Whether the method was called from a setter method. Defaults to `False`.

        Returns:
            None
        """

        self.internal("Setting log levels")

        if not call_from_setter:

            # If we received a console level, update the console level.
            if console_level is not None:
                self.console_level = console_level

            # If we received a file level, update the file level.
            if file_level is not None:
                self.file_level = file_level

        if console_level is not None:
            self.__apply_level_change('console')

        if file_level is not None:
            self.__apply_level_change('file')

    @method_alias('add_child', 'add_child_logger', 'get_child_logger')
    def get_child(self, name=None, console_level=None, file_level=None, **kwargs) -> InspyLogger:
        """
        Retrieves or creates a nested child logger based on a dot-separated name.
    

        Parameters:
            name (str, optional):
                Dot-separated name representing the hierarchy of child loggers.
                E.g., 'child.method' will create or retrieve 'child' and then 'method' as nested children.
    
            console_level (int or str, optional):
                Console log level for the child logger(s).
    
            file_level (int or str, optional):
                File log level for the child logger(s).
    
        Returns:
            InspyLogger:
                The deepest child logger in the hierarchy specified by the name.
        """
        if name is None:
            # Get the name from the caller's function if not provided
            caller_frame = inspect.stack()[1]
            name = self.__build_name_from_caller(caller_frame, name)

        name_parts = name.split('.')
        current_logger = self

        for part in name_parts:
            # Build the full name for the child logger
            cl_name = f"{current_logger.name}.{part}"

            if found_child := current_logger.find_child_by_name(
                cl_name, exact_match=True
            ):
                current_logger = found_child
            else:
                # Create a new child logger
                console_level = console_level or current_logger.console_level
                file_level = file_level or current_logger.file_level

                child_logger = Logger(
                    name=cl_name,
                    console_level=console_level,
                    file_level=file_level,
                    parent=current_logger,
                    **kwargs
                )
                current_logger.children.append(child_logger)
                current_logger = child_logger

        return current_logger


    @method_alias('get_children_names', 'get_child_loggers')
    def get_child_names(self) -> List:
        """
        Fetches the names of all child loggers associated with this logger instance.
        """

        self.internal("Getting child logger names")
        return [child.name for child in self.children]

    def get_parent(self) -> InspyLogger:
        """
        Fetches the parent logger associated with this logger instance.
        """

        self.internal("Getting parent logger")
        return self.parent

    def find_child_by_name(self, name: str, case_sensitive=True, exact_match=False) -> (List, InspyLogger):
        """
        Searches for a child logger by its name.

        Parameters:
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
        self.internal(f'Searching for child with name: {name}')
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
    def debug(self, message, *args, stack_level=2, **kwargs):
        """
        Logs a debug message.

        Parameters:
            message (str): The message to log.

            stack_level (int, optional):
                The stacklevel to use when logging. Defaults to 3.
        """
        self._log(logging.DEBUG, message, args=args, stacklevel=stack_level, **kwargs)

    @count_invocations
    def info(self, message, *args, stack_level=2, **kwargs):
        """
        Logs an info message.

        Parameters:
            message (str):
                The message to log.

            stack_level (int, optional):
                The stack-level to use when logging. Defaults to 2.

        Returns:
            None
        """
        self._log(logging.INFO, message, args=args, stacklevel=stack_level, **kwargs)

    def internal(self, message, *args, stack_level=2, **kwargs):
        """
        Logs an internal message.

        Parameters:
            message (str):
                The message to log.

            stack_level (int, optional):
                The stack-level to use when logging. Defaults to 2.
        """
        if self.logger.isEnabledFor(INTERNAL):
            self._log(INTERNAL, message, args=args, stacklevel=stack_level, **kwargs)

    @count_invocations
    def warning(self, message, *args, stack_level=2, **kwargs):
        """
        Logs a warning message.

        Parameters:
            message (str):
                The message to log.

            stack_level (int, optional):
                The stack-level to use when logging. Defaults to 2.

        Returns:
            None

        """
        self._log(logging.WARNING, message, args=args, stacklevel=stack_level, **kwargs)

    @count_invocations
    def error(self, message, *args, stack_level=2, **kwargs):
        """
        Logs an error message.

        Parameters:
            message (str):
                The message to log.

            stack_level (int, optional):
                The stack-level to use when logging. Defaults to 2.

        Returns:
            None
        """
        self._log(logging.ERROR, message, args=(), stacklevel=2, **kwargs)

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

    def announce_initialization(
            self,
            message_level: str = None,
            do_replace_placeholders=True,
            ):
        """
        Announces the initialization of the logger.

        Parameters:
            message_level (str, optional):
                The logging level to use for the announcement. Defaults to 'debug'.

            do_replace_placeholders (bool, optional):
                Whether to replace placeholders in the announcement. Defaults to True.

        Returns:
            None
        """
        if self.announcement_made:
            return

        if do_replace_placeholders:
            self.announcement.replace_placeholders()

        if message_level is None:
            message_level = self.announcement_level

        self.announcement.announcement_level = message_level

        self.announcement.announce()

    @classmethod
    def create_logger_for_caller(cls):
        """
        Creates a logger for the module that calls this method.

        Returns:
            Logger: An instance of the Logger class for the calling module.
        """
        if 'ipkernel' in sys.modules or 'IPython' in sys.modules:
            # We're running in an interactive environment, return a logger named 'interactive'

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
                'Name':              self.name,
                'Console Level':     self.console_level_name,
                'File Level':        self.file_level_name,
                'Parent':            self.parent.name if self.parent else 'None',
                'Children':          {
                        'Count':   len(self.children),
                        'Names':   self.child_names,
                        'Loggers': [child.to_dict() for child in self.children]
                        },
                'Handlers':          {
                        'Count':    len(self.logger.handlers),
                        'Handlers': self.logger.handlers
                        },
                'Call Counts':       self.call_counts,
                'Buffering Handler': 'Yes' if getattr(self, 'buffering_handler', None) else 'No'
                }

    def start(self):
        """
        Starts the logger.
        """
        self.warning('InspyLogger.start() is deprecated.')
        if not self.logger.handlers:
            self.set_up_handlers()

        if hasattr(self, 'buffering_handler'):
            self.replay_and_setup_handlers()

        return self

    def warn_once(self, message):
        """
        Logs a warning message only once.

        Parameters:
            message:
                The warning message to be logged.

        Returns:
            None
        """
        if message not in self.__warnings_issued:
            self.warning(message)
            self.warnings_issued.add(message)

    @staticmethod
    def _determine_module_path(frame):
        """
        Determines the in-project path of the module from the call frame.

        Parameters:
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
        # caller_frame = inspect.currentframe().f_back
        if INTERACTIVE_SESSION:
            stacklevel -= 1

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

        if call_counts_str := ', '.join(
                f'{method}: {count}' for method, count in self.call_counts.items()
                ):
            table.add_row('Call Counts', call_counts_str)
        else:
            table.add_row('Call Counts', 'No method calls recorded')

        if getattr(self, 'buffering_handler', None):
            table.add_row('Buffering Handler', 'Yes' if self.buffering_handler else 'No')

        return table


def get_loggers():
    import gc

    gc.collect()
    loggers = [obj for obj in gc.get_objects() if isinstance(obj, InspyLogger)]

    return {str(logger).split(": ")[1].split(" w/")[0]: logger for logger in loggers}
