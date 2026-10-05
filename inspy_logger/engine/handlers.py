import logging
from logging import Handler

from rich.logging import RichHandler

from inspy_logger.helpers import CustomFormatter


class BufferingHandler(Handler):

    def __init__(self):
        super().__init__()
        self.buffer = []
        self.replaying = False

    def emit(self, record):
        if not self.replaying:
            self.buffer.append(record)

    def replay_logs(self, logger):
        """
        Replays the buffered logs and restores the original logging level of the logger.

        Parameters:
            logger:
                The logger instance to replay the logs to.

        Returns:
            None

        Examples:
            >>> handler = BufferingHandler()
            >>> logger = logging.getLogger()
            >>> logger.addHandler(handler)
            >>> logger.setLevel(logging.DEBUG)
            >>> logger.debug("Debug message")
            >>> logger.info("Info message")
            >>> logger.warning("Warning message")
            >>> handler.replay_logs(logger)
            # The buffered logs are replayed to the logger and the original logging level is restored.
        """

        self.replaying = True
        orig_level = logger.level
        logger.setLevel(logging.CRITICAL)

        for record in self.buffer:
            logger.handle(record)

        self.buffer.clear()

        self.replaying = False

        logger.setLevel(orig_level)


class HandlerConfigurator:
    """Configure handlers and keep the wrapped logger's level permissive."""

    def __init__(self, owner):
        self.owner = owner

    def sync_logger_level(self):
        """Allow every record accepted by at least one enabled handler."""
        levels = [self.owner.console_level]
        if not self.owner.no_file_logging:
            levels.append(self.owner.file_level)
        self.owner.logger.setLevel(min(levels))

    def apply_level_change(self, handler_type):
        level = getattr(self.owner, f"{handler_type}_level")
        handler_class = RichHandler if handler_type == "console" else logging.FileHandler

        for handler in self.owner.logger.handlers:
            if isinstance(handler, handler_class):
                handler.setLevel(level)

        self.sync_logger_level()

    def ensure_log_file_path(self):
        if self.owner.no_file_logging:
            return
        if not self.owner.file_path.exists():
            self.owner.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.owner.file_path.touch()

    def set_up_console(self):
        if any(isinstance(handler, RichHandler) for handler in self.owner.logger.handlers):
            return

        console_handler = RichHandler(
            show_level=True,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
        )
        console_handler.setFormatter(
            CustomFormatter(f"[{self.owner.logger.name}] %(message)s")
        )
        console_handler.setLevel(self.owner.console_level)
        self.owner.logger.addHandler(console_handler)
        self.sync_logger_level()

    def set_up_file(self):
        if self.owner.no_file_logging:
            self.remove_file_handlers()
            self.sync_logger_level()
            return
        if any(
            isinstance(handler, logging.FileHandler)
            for handler in self.owner.logger.handlers
        ):
            return

        self.ensure_log_file_path()
        file_handler = logging.FileHandler(self.owner.file_path)
        file_handler.setLevel(self.owner.file_level)
        file_handler.setFormatter(
            CustomFormatter(
                "%(asctime)s - [%(name)s] - %(levelname)s - "
                "%(message)s |-| %(pathname)s:%(lineno)d"
            )
        )
        self.owner.logger.addHandler(file_handler)
        self.sync_logger_level()

    def remove_file_handlers(self):
        for handler in list(self.owner.logger.handlers):
            if isinstance(handler, logging.FileHandler):
                self.owner.logger.removeHandler(handler)
                handler.close()

    def set_up_handlers(self):
        self.set_up_console()
        self.set_up_file()
        self.sync_logger_level()
