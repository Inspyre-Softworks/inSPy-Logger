from logging import Handler
import logging


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

        Args:
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
