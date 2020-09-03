#!/usr/bin/env python3
"""

This package contains a class that will create and maintain a logging device for you

Returns:
    InspyLogger: A colored and formatted logging device.
"""

import logging, colorlog
from colorlog import ColoredFormatter
from logging import DEBUG, INFO, WARNING, getLogger, Logger

LEVELS = ["debug", "info", "warning"]
"""The names of the log output levels one can pick from"""

class InspyLogger(Logger):
    """
        Starts a colored and formatted logging device for you.

        Starts a colored and formatted logging device for you. No need to worry about handlers, etc

        Args:

            device_name (str): A string containing the name you'd like to choose for the root logger

            log_level (str): A string containing the name of the level you'd like InspyLogger to be limited to. You can choose between:

              - debug
              - info
              - warning
     """
    def adjust_level(self, l_lvl):
        """

        Adjust the level of the logger associated with this instance.

        Args:
            l_lvl (): A string containing the name of the level you'd like InspyLogger to be limited to. You can choose between:

              - debug
              - info
              - warning

        Returns:
            None

        """

        _log = getLogger(self.root_name)

        if l_lvl == "debug":
            _ = DEBUG
        elif l_lvl == "info":
            _ = INFO
        elif l_lvl == "warn" or l_lvl == "warning":
            _ = WARNING

        _log.setLevel(_)

    def __start__(self):
        """

        Start the actual logging instance and fill the attributes that __init__ creates.

        Returns:
            None

        """
        if self.started:
            self.device.warning(
                "There already is a base logger for this program. I am using it to deliever this message."
            )
            return None

        formatter = ColoredFormatter(
            "%(bold_cyan)s%(asctime)-s%(reset)s%(log_color)s::%(name)s%(module)-14s::%(levelname)-10s%(reset)s%("
            "blue)s%(message)-s",
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "bold_cyan",
                "INFO": "bold_green",
                "WARNING": "bold_yellow",
                "ERROR": "bold_red",
                "CRITICAL": "bold_red",
            },
        )

        self.device = logging.getLogger(self.root_name)
        self.main_handler = logging.StreamHandler()
        self.main_handler.setFormatter(formatter)
        self.device.addHandler(self.main_handler)
        self.adjust_level()
        self.device.info(f"Logger started for %s" % self.root_name)
        self.started = True

    def __init__(self, device_name, log_level):
        """
        Starts a colored and formatted logging device for you.

        Starts a colored and formatted logging device for you. No need to worry about handlers, etc

        Args:

            device_name (str): A string containing the name you'd like to choose for the root logger

            log_level (str): A string containing the name of the level you'd like InspyLogger to be limited to.
            You can choose between:
              - debug
              - info
              - warning
    """

        if log_level is None:
            log_level = "info"
        self.l_lvl = log_level.lower()
        self.root_name = device_name
        self.started = False
        self.device = None
        self.__start__()

