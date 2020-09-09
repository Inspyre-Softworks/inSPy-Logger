#!/usr/bin/env python3
"""

This package contains a class that will create and maintain a logging device for you

Returns:
    InspyLogger: A colored and formatted logging device.

"""

import logging, colorlog, inspect
from colorlog import ColoredFormatter
from logging import DEBUG, INFO, WARNING, getLogger, Logger

import pkg_resources
from pkg_resources import DistributionNotFound
from packaging import version as pkg_ver
import sys
import luddite
from luddite import get_version_pypi, get_versions_pypi

pretty_name = "InSPy Logger"
pkg_name = __package__
py_ver = sys.version.split(" ")[0]


def __get_version__(pkg_name):
    try:
        ver = pkg_resources.get_distribution(pkg_name).version
    except DistributionNotFound as e:
        statement = f"{str(e)}!"
        print(statement)
        ver = "Unknown"

    is_latest = get_version_pypi(pkg_name) == ver

    if is_latest:
        update_statement = "You are up to date!"
    else:
        if pkg_ver.parse(str(ver)) < pkg_ver.parse(str(get_version_pypi(pkg_name))):
            update_statement = f"You are running an older version of {pkg_name} than what is available. Consider upgrading."
        else:
            if ver in get_versions_pypi(pkg_name):
                avail_ver = (
                    ", a developmental version available via the PyPi repository"
                )
            else:
                avail_ver = (
                    ", a version that is NOT available via any online package manager"
                )
            update_statement = f"You are running a version of {pkg_name} that is newer than the latest version{avail_ver}"
            update_statement += f"\nThe versions available from PyPi are: {', '.join(get_versions_pypi(pkg_name))}"

    ver = str(f"{pretty_name} ({ver}) using Python {py_ver}\n" + f"{update_statement}")

    return ver


__VERSION__ = __get_version__(__package__)

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

    def adjust_level(self, l_lvl="info", silence_notif=False):
        """

        Adjust the level of the logger associated with this instance.

        Args:
            l_lvl (str): A string containing the name of the level you'd like InspyLogger to be limited to. You can choose between:

              - debug
              - info
              - warning

            silence_notif (bool): Silence notifications (of 'info' level) when adjusting the logger's level. True for
            no output and False to get these notifications.

        Returns:
            None

        """

        _log = getLogger(self.root_name)

        _caller = inspect.stack()[1][3]

        if self.last_lvl_change_by is None:
            _log.info("Setting logger level for first time")
            _log.debug("Signing in")
            self.last_lvl_change_by = "Starting Logger"
        else:
            if not silence_notif:
                _log.info(
                    f"{_caller} is changing logger level from {self.l_lvl} to {l_lvl}"
                )
                _log.info(
                    f"Last level change was implemented by: {self.last_lvl_change_by}"
                )
                _log.info(f"Updating last level changer")

            self.last_lvl_change_by = _caller

        self.l_lvl = l_lvl

        if self.l_lvl == "debug":
            _ = DEBUG
        elif self.l_lvl == "info":
            _ = INFO
        elif self.l_lvl == "warn" or self.l_lvl == "warning":
            _ = WARNING

        _log.setLevel(_)

    def start(self, mute=False, no_version=False):
        """

        Start the actual logging instance and fill the attributes that __init__ creates.

        Arguments:

            mute (bool): Mute all output that starting the root-logger would produce. True: No output on executing start() | False: Do not suppress all output

            no_version (bool): If you start the logger using the 'debug' log-level the logger will output its own version information. True: Suppress this output, no matter the log-level | False: Do no suppress this output

        Note:
            If you give the 'mute' parameter a value of `True` then the value of the `no_version` parameter will be ignored.

        Returns:
            None

        """
        if self.started:
            self.device.warning(
                "There already is a base logger for this program. I am using it to deliver this message."
            )
            return None

        formatter = ColoredFormatter(
            "%(bold_cyan)s%(asctime)-s%(reset)s%(log_color)s::%(name)s.%(module)-14s::%(levelname)-10s%(reset)s%("
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
        self.adjust_level(self.l_lvl)
        _log_ = logging.getLogger(self.root_name + ".InspyLoggerDevice")
        if not mute:
            _log_.info(f"Logger started for %s" % self.root_name)
            if not no_version:
                _log_.debug(
                    f"\nLogger Info:\n" + ("*" * 35) + f"\n{__VERSION__}\n" + ("*" * 35)
                )
                self.started = True

        # self.manifest += 'root': {

        # }

        return self.device

    def __init__(self, device_name, log_level):
        """

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
        self.last_lvl_change_by = None
        self.device = None
        self.manifest = {}
