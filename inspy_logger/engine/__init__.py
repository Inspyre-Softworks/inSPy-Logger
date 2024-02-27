import inspect
import os
import logging
from rich.logging import RichHandler
from inspy_logger.engine.handlers import BufferingHandler
from inspy_logger.common import InspyLogger, DEFAULT_LOGGING_LEVEL
from inspy_logger.helpers import translate_to_logging_level, CustomFormatter, get_level_name
from typing import List


class Logger(InspyLogger):
    """
    A Singleton class responsible for managing the logging mechanisms of the application.
    """

    instances = {}  # A dictionary to hold instances of the Logger class.
    __started = False

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
            auto_start=False,
            console_level=DEFAULT_LOGGING_LEVEL,
            file_level=logging.DEBUG,
            filename="app.log",
            parent=None,
    ):
        """
        Initializes a logger instance.

        Args:
            name (str):
                The name of the logger instance.

            auto_start (bool):
                Should the logger start upon initialization. THIS CANNOT BE SET AFTER INITIALIZATION!

            console_level (str, optional):
                The logging level for the console. Defaults to DEFAULT_LOGGING_LEVEL.

            file_level (str, optional):
                The logging level for the file. Defaults to logging.DEBUG.

            filename (str, optional):
                The name of the log file. Defaults to "app.log".

            parent (Logger, optional):
                The parent logger instance. Defaults to None.
        """
        # Check if the logger has already been initialized.
        if hasattr(self, 'logger'):
            return

        self.__auto_start = False
        self.__name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(console_level)

        # Add the buffering handler
        self.buffering_handler = BufferingHandler()
        self.logger.addHandler(self.buffering_handler)
        self.logger.debug('Initializing logger')

        self.__console_level = console_level
        self.filename = filename
        self.__file_level = file_level or DEFAULT_LOGGING_LEVEL
        self.parent = parent

        self.logger.propagate = False

        self.children = []

        self.__auto_start = auto_start

        if self.auto_start:
            self.start()

    @property
    def auto_start(self):
        return self.__auto_start

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
        self.set_level(console_level=level)

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
        return self.logger

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
        self.set_level(file_level=level)

    @property
    def file_level_name(self):
        return get_level_name(self.file_level)

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
    def started(self):
        return self.__started

    @started.setter
    def started(self, new: bool):
        """
        Internal setter to set `started` with caller check.

        Note:
            This setter can only be used by members of this class!

        Raises:
            AttributeError:
               When a non-class member attempts to use this setter.

        """
        if not isinstance(new, bool):
            raise TypeError(f'`started` must be of type `bool` not {type(new).__name__}')
        
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name
        caller_self = caller_frame.f_locals.get('self', None)

        if not isinstance(caller_self, Logger) or caller_name.startswith('_'):
            raise AttributeError('This property can only be set from within the class!')

        self.__started = new


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

        self.logger.debug("Setting up file handler")
        file_handler = logging.FileHandler(self.filename)
        file_handler.setLevel(self.__file_level)
        formatter = CustomFormatter(
            "%(asctime)s - [%(name)s] - %(levelname)s - %(message)s |-| %(filename)s:%(lineno)d"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def set_level(self, console_level=None, file_level=None) -> None:
        """
        Updates the logging levels for both console and file handlers.
        """

        self.logger.debug("Setting log levels")
        if console_level is not None:
            console_level = translate_to_logging_level(console_level)
            self.logger.handlers[0].setLevel(console_level)
            for child in self.children:
                child.set_level(console_level=console_level)

            self.__console_level = console_level

        if file_level is not None:
            file_level = translate_to_logging_level(file_level)
            self.logger.handlers[1].setLevel(file_level)
            for child in self.children:
                child.set_level(file_level=file_level)

            self.__file_level = file_level

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
        if console_level is not None:
            console_level = translate_to_logging_level(console_level)

        if file_level is not None:
            file_level = translate_to_logging_level(file_level)

        console_level = console_level or self.console_level
        caller_frame = inspect.stack()[1]

        if name is None:
            name = caller_frame.function

        caller_self = caller_frame.frame.f_locals.get("self", None)
        separator = ":" if caller_self and hasattr(caller_self, name) else "."
        child_logger_name = f"{self.logger.name}{separator}{name}"

        for child in self.children:
            if child.logger.name == child_logger_name:
                return child

        child_logger = Logger(name=child_logger_name, console_level=console_level, file_level=file_level, parent=self)

        self.children.append(child_logger)

        child_logger.started = self.started

        if self.started:
            child_logger.replay_and_setup_handlers()

        return child_logger

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

    def debug(self, message):
        """
        Logs a debug message.

        Args:
          message (str): The message to log.
        """
        self._log(logging.DEBUG, message, args=(), stacklevel=2)

    def info(self, message):
        """
        Logs an info message.

        Args:
            message (str): The message to log.
        """
        self._log(logging.INFO, message, args=(), stacklevel=2)

    def warning(self, message):
        """
        Logs a warning message.


        Args:
            message (str): The message to log.
        """
        self._log(logging.WARNING, message, args=(), stacklevel=2)

    def error(self, message):
        """
        Logs an error message.


        Args:
            message (str): The message to log.
        """
        self._log(logging.ERROR, message, args=(), stacklevel=2)

    def start(self):
        if self.started:
            return

        self.replay_and_setup_handlers()
        self.started = True

        for child in self.children:
            child.started = True
        
        

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
        frame = inspect.currentframe().f_back
        if module_path := cls._determine_module_path(frame):
            return cls(module_path)
        else:
            raise ValueError("Unable to determine module path for logger creation.")

    def replay_and_setup_handlers(self):
        """
        Replays the buffered logs and sets up the handlers for the logger.
        """
        if self.buffering_handler:
            self.buffering_handler.replay_logs(self.logger)

            # Remove the buffer handler
            self.logger.removeHandler(self.buffering_handler)

            self.set_up_console()
            self.set_up_file()

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
