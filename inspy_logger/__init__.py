#!/usr/bin/env python3
"""

This package contains a class that will create and maintain a logging device for you

Returns:
    InspyLogger: A colored and formatted logging device.

"""

import inspect
import logging
import sys
import time
from logging import DEBUG, INFO, Logger, WARNING, getLogger
from urllib.error import URLError

from colorlog import ColoredFormatter
from luddite import get_version_pypi
from pkg_resources import DistributionNotFound

from inspy_logger.errors import ManifestEntryExistsError, DeviceNotStartedError, DeviceAlreadyStartedError
from inspy_logger.helpers.network import check_connectivity

#####################################
## MOST ACCURATE VERSION INDICATOR ##
#####################################

RELEASE = "2.1"

VERSION = "2.1"

ON_REPO = True

#####################################
######## VERSION DATA ABOVE! ########
#####################################

pretty_name = "InSPy Logger"
PKG_NAME = __package__
PY_VER = sys.version.split(" ")[0]

LEVELS = ["debug", "info", "warning"]
"""The names of the log output levels one can pick from"""

latest_version = "Please start the InspyLogger class"

islatest = None


class InspyLogger(object):
    """ InspyLogger is meant to be a shortcut to a program-wide logger with levels and ease-of-use. """

    class Version:

        def __init__(self):
            """

            This class helps manage the Version information for InspyLogger

            """

            self.package_name = "InSPy-Logger"
            """The name of the program"""

            self.local = VERSION
            """
            The hard-coded version of the program. Unless this is changed by someone 
            other than the developers 
            """

            self.__is_up_to_date = None

            self.__needs_update = None
            self.__offline = None

            self.optional_update = None
            self.latest_stable = None
            self.latest_pr = None
            self.offline = False

        @property
        def needs_update(self):
            """
            The needs_update function checks whether the package version is up to date with
            the latest version on PyPI. If it is not, then it returns True, otherwise False.

            Returns:
                * True:
                    The local package version does not match the latest version available via Pypi.
                * False:
                    The local package version matches or exceeds the latest version available via Pypi.
            """
            if self.__needs_update is None or self.__is_up_to_date is None:
                return self.is_up_to_date

        @staticmethod
        def __instruction_feeder(instruct_group):
            for line in instruct_group:
                print(line)

        @property
        def is_up_to_date(self):
            """

            Checks with PyPi to make sure you have the latest version.

            Returns:

                * This function will return three fields with varying values which are the following in respective order:
                    - Is the local version at least up to date with the latest stable version found on PyPi? (In the form of a boolean)
                    - A string that best matches the update status of InspyLogger.
                        * The possible values are:

                            - match: Matches the latest stable version, not pre-release

                            - pr_ver: The version number is a pre-release, as it's number is greater than the latest stable copy available on Pypi

                            - not_released: The version number not only exceeds the latest stable version on PyPi but also the latest Pre-Release copy available on PyPi

                            - outdated: The version number is less than the latest stable version available on PyPi

                One of three possible results:


                    - (bool : True, str : `match`, obj : VERSION)

                        Indicates that this version number matches the copy on PyPi

                    - (True (bool), "pr_ver", VERSION):
                    Indicates that a "Pre-Release" version of InSPy-Logger is being used and matches a release found on PyPi
                    - (False (bool), "not_released", VERSION): Indicates that this version number surpasses the highest available on PyPi
                    - (False (bool), "outdated", VERSION):  Indicates that this version number is lower than the latest stable version on PyPi

            """

            latest = self.get_latest()

            if latest is None and self.offline:
                self.latest_stable = ("Unknown", "Offline")
                self.latest_pr = ("Unknown", "Offline")
                self.__needs_update = ("Unknown", "Offline")
                self.optional_update = False
            if not self.offline and self.needs_update is not None and self.needs_update:
                notif_lines = [
                        "An update for InSPy-Logger is available! Please update!",
                        "You can update in one of the following ways:"
                ]

                direct_update_instructions = [
                        "    - Through the package itself:",
                        "        from inspy_logger import InspyLogger, LogDevice",
                        "        ",
                        "        i_log = InspyLogger()",
                        "        iLog_ver = i_log.Version()",
                        "        iLog_ver.update(pr=False)",
                ]

                pypi_update_instructions = [
                        "    - Through your system's implementation of PIP",
                        "        $> python3 -m pip install --update inspy_logger",
                        "        OR",
                        "        $> python3 -m pip install inspy_logger VER"
                ]

                border = str("*-*" * 20)
                # Notify the user through the console of an update being available.
                print(notif_lines)

                print(border)

                self.__instruction_feeder(direct_update_instructions)

                print("-|-" * 20)

                self.__instruction_feeder(pypi_update_instructions)

                print(border)

                return False, "outdated", self.local

            # If the constant ON_REPO is Bool(False) we'll assume it's a pre-release
            if not ON_REPO:
                return True, "pr_ver", self.local

        def get_latest(self):
            try:
                return get_version_pypi(self.package_name)
            except URLError:
                statement = "Unable to access distribution server. Seeing if network is down..."
                print(statement)
                if not check_connectivity():
                    statement = "Unable to connect to the internet, therefore I can't get remote version data"
                    print(statement)
                    self.offline = False
                else:
                    statement = "Able to access the internet, however there's no access to the version data server...."
                    print(statement)
                    self.offline = True
                ver = "Unknown"
                self.__is_up_to_date = False
                self.offline = True
                return None
            except DistributionNotFound:
                ver = "Unknown"
                is_latest = False

            return ver, is_latest

    def __init__(self, log_name=None, log_level=None, autostart=False, start_on_device_call=False):
        self.__auto_start = autostart

        self.loc_version = self.Version()  # 'loc' = short for 'local' for the curious

        self.root_name = 'InspyLogger'

        self.__loc_version = None

        self.__name = log_name

        self.__level = log_level

        if log_level is None:
            self.__level = 'INFO'

        self.__device = None

        self.__VERSION = None

        self.__root_device = None

        self.__start_on_device_call = start_on_device_call

        if log_name:
            self.device = self.LogDevice(log_name, log_level)

            if self.__auto_start and not self.device.started:
                self.device.start()
        else:
            self.dev

    @property
    def name(self) -> (str | None):
        """
        The name of the logging device.
        """
        return self.__name

    @name.setter
    def name(self, new: (str | None)):
        if self.__device is not None and self.device.started:
            raise DeviceAlreadyStartedError('You cannot change the name of a running log device. Try adding a '
                                            'child device?')
        self.__name = new

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, new):
        if self.device is None:
            raise DeviceNotStartedError()
        if isinstance(self.device, self.LogDevice):
            self.device.adjust_level(new)
        else:
            raise TypeError("device must be a LogDevice instance!")

    @property
    def autostart(self):
        return self.__auto_start

    @autostart.setter
    def autostart(self, new):
        if self.device is not None and not self.device.started:
            if isinstance(new, bool):\
                self.__auto_start = new
            else:
                raise TypeError('Autostart must be a boolean value')
        elif self.device.started:
             raise DeviceAlreadyStartedError('Setting "autostart" would do no good.')

    @property
    def start_on_device_call(self):
        return self.__start_on_device_call

    @start_on_device_call.setter
    def start_on_device_call(self, new):
        if not isinstance(new, bool):
            raise TypeError('start_on_device_call must be a boolean value!')

        self.__start_on_device_call = new

    @property
    def device(self):
        if self.__device is not None and not self.__device.started and self.start_on_device_call:
            self.device.start()

        return self.__device

    @device.setter
    def device(self, new):
        if not isinstance(new, self.LogDevice):
            raise TypeError('Device must be an InspyLogger.LogDevice instance!')

        self.__device = new

    @property
    def local_version(self):
        """
        The local_version function is a property that returns the local version of the package.
        It is used to determine if there are any updates available on PyPI.
        """

        if self.__loc_version is None:
            self.__loc_version = self.Version()

        return self.__loc_version

    @property
    def VERSION(self):
        """
        The VERSION function is used to return the version of the package.
        It will first check if a local version has been set, and if not it will
        return the pypi version.

        Returns:

            The version of the local package
        """

        if self.__VERSION is None:
            self.__VERSION = self.local_version.local

        return self.__VERSION

    # def __get_version(self, pkg_name):
    #     """
    #     The :func:`__get_version` function is used to print the version of the package and
    #     the versions available from PyPi.

    #     It also prints whether or not there are developmental versions available. If there
    #     are developmental versions, it will also print a warning that these should not be
    #     used in production.

    #     Arguments:

    #         pkg_name (str):
    #             The name of the package you're seeking the version of. (Required)

    #     Returns:
    #         A string that contains the name of the package, it's version number,
    #         and a statement about whether or not the target package's local
    #         version should be updated.

    #     """

    #     if self.loc_version.is_up_to_date:
    #         update_statement = "You are up to date!"
    #     else:
    #         if pkg_ver.parse(str(self.VERSION)) < pkg_ver.parse(str(get_version_pypi(pkg_name))):
    #             update_statement = f"You are running an older version of {pkg_name} than what is available. Consider upgrading."
    #         else:
    #             if self.VERSION in get_versions_pypi(pkg_name):
    #                 avail_ver = (
    #                     ", a developmental version available via the PyPi repository"
    #                 )
    #             else:
    #                 avail_ver = (
    #                     ", a version that is NOT available via any online package manager"
    #                 )
    #             update_statement = f"You are running a version of {pkg_name} that is newer than the latest version{avail_ver}"
    #             update_statement += f"\nThe versions available from PyPi are: {', '.join(get_versions_pypi(pkg_name))}"

    #     ver = str(f"{pretty_name} ({self.VERSION}) using Python {PY_VER}\n" + f"{update_statement}")

    #     print(ver)

    #     return ver

    class LogDevice(Logger):
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

        def __add_child(self, name: str):
            # Start a logger for this function
            log = getLogger(f"{self.own_logger_root_name}.add_child")
            ts = time.time()
            frame = inspect.stack()[1]

            frame_name = frame[3]

            line_no = frame[2]

            file_name = frame[1]

            root_name = self.root_name

            log.debug(
                "Received request to add %(name)s to %(root_name)s by %(frame_name)s on line %(line_no)s of %(file_name)s.")
            log.debug("Full Frame Info ")

            if existing := next((sub for sub in self.manifest if sub['child_name'].lower() == name.lower()), None):
                try:
                    raise ManifestEntryExistsError()
                except ManifestEntryExistsError as e:
                    log.warning(e.message)
                    return existing

            # Assemble a manifest entry.
            manifest_entry = {
                    "child_name":   name,
                    "caller_file":  file_name,
                    "calling_line": line_no,
                    "created_ts":   ts
            }

            self.manifest.append(manifest_entry)

            return getLogger(f"{name}")

        def add_child(self, name: str):
            """

            Create (and return) a child logger under the root log device. Also add it to the manifest to keep track of it.

            Args:
                name (str): The name you'd like to give the child logger

            Returns:
                getLogger: A child logging device.

            """

            return self.__add_child(name)

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
                last_level = self.level
                last_level_change_by = self.last_lvl_change_by
            else:
                if not silence_notif:
                    _log.info(
                        "%(_caller)s is changing logger level from %(last_level)s to %(l_lvl)s",
                    )

                    _log.info(
                        "Last level change was implemented by: %(last_level_change_by)s"
                    )

                    _log.info("Updating last level changer")

                self.last_lvl_change_by = _caller

            self.level = l_lvl

            if isinstance(self.level, int):
                new_lvl = self.level
            else:
                new_lvl = None

                if self.level.lower() == "debug":
                    new_lvl = DEBUG
                elif self.level.lower() == "info":
                    new_lvl = INFO
                elif self.level.lower() in ["warn", "warning"]:
                    new_lvl = WARNING

            _log.setLevel(new_lvl)

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
                datefmt = None,
                reset = True,
                log_colors = {
                        "DEBUG":    "bold_cyan",
                        "INFO":     "bold_green",
                        "WARNING":  "bold_yellow",
                        "ERROR":    "bold_red",
                        "CRITICAL": "bold_red",
                },
            )

            self.device = logging.getLogger(self.root_name)
            self.main_handler = logging.StreamHandler()
            self.main_handler.setFormatter(formatter)
            self.device.addHandler(self.main_handler)
            self.adjust_level(self.level)
            _log_ = logging.getLogger(self.own_logger_root_name)
            if not mute:
                _log_.info(f"Logger started for {self.root_name}")
                if not no_version:
                    _log_.debug(
                        f"\nLogger Info:\n" +
                        ("*" * 35) + f"\n{VERSION}\n" + ("*" * 35)
                    )
                    self.__started = True

            return self.device

        def __init__(self, log_name, log_level=None):
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
                log_level = 'INFO'

            self.__device_name = log_name

            self.__started = False
            self.__level = log_level

            self.root_name = self.name
            self.own_logger_root_name = f"{self.root_name}.InSPyLogger"
            super(InspyLogger.LogDevice, self).__init__(name = self.own_logger_root_name, level = self.level.upper())

            self.last_lvl_change_by = None
            self.device = None
            self.manifest = []
            self.main_handler = None

        @property
        def name(self):
            """
            The name of the logging device.

            Returns:
                (str | None): The name of the logging device.

            """
            return self.__device_name

        @name.setter
        def name(self, new):
            if not self.__device_name:
                self.__device_name = new

        @property
        def level(self):
            return self.__level

        @level.setter
        def level(self, new):
            self.__level = new

        @property
        def started(self):
            """
            Indicates whether the logging device has been started or not yet.

            Returns:
                * :bool:`True`:
                    Returned if the device has been started.

                * :bool:`False`:
                    Returned if the device has not yet been started.

            Note:
              :property:`InspyLogger().LogDevice().started` is a read-only property.

            """
            return self.__started
