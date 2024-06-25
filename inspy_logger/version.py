import requests
import packaging
from packaging import version as pkg_version

RELEASE_MAP = {
    'dev': 'Development Build',
    'alpha': 'Alpha Build',
    'beta': 'Beta Build',
    'rc': 'Release Candidate Build',
    'final': 'Final Release Build'
}


__VERSION__ = {
    'major': 3,
    'minor': 1,
    'patch': 1,
    'release': 'final',
    'release_num': 0
}


def parse_version():
    """
    Parses the version information into a string.

    Returns:
        str: The version information.

    Since:
        v1.0
    """
    version = f'{__VERSION__["major"]}.{__VERSION__["minor"]}.{__VERSION__["patch"]}'

    if __VERSION__['release'] != 'final':
        version += f'-{__VERSION__["release"]}.{__VERSION__["release_num"]}'

    return version


def get_full_version_name():
    """
    Gets the full version name.

    Returns:
        str: The full version name.

    Since:
        v1.0
    """
    ver = parse_version()
    ver = ver.split('-')[0]

    release_type = RELEASE_MAP[__VERSION__["release"]]
    release_num = __VERSION__["release_num"]
    release_str = f" {release_type} {'' if __VERSION__['release'].lower() == 'final' else f'({release_num})'}"
    return f'v{ver}{release_str}'

def get_pypi_info():
    """
    Gets the latest version information from PyPI.

    Returns:
        dict: The latest version information.

    Since:
        v1.0
    """
    url = 'https://pypi.org/pypi/inspy-logger/json'
    resp = requests.get(url)
    resp.raise_for_status()
    resp = resp.json()
    return resp


class PyPiVersionInfo:
    """
    A class to represent the version information for this package from PyPi.

    Attributes:
        latest_stable (str):
            The latest stable version of the package on PyPi.

        latest_pre_release (str):
            The latest pre-release version of the package.
    Since:
        v3.0
    """
    __url                                  = 'https://pypi.org/pypi/inspy-logger/json'
    __queried                              = False
    __installed                            = parse_version()
    __include_pre_release_for_update_check = False
    __new_version_available_num            = None
    __checked_for_update                   = False
    __installed_newer_than_latest          = None

    def __init__(self, include_pre_release_for_update_check=__include_pre_release_for_update_check):
        self.__latest_stable = None
        self.__latest_pre_release = None

        self.__all_versions = None

        self.include_pre_release_for_update_check = include_pre_release_for_update_check

        self.__query_versions()

    @property
    def all_versions(self):
        return self.__all_versions

    @property
    def checked_for_update(self):
        return self.__checked_for_update

    @property
    def include_pre_release_for_update_check(self):
        """
        Gets whether pre-release versions should be included when checking for updates.

        Returns:
            bool:
                True if pre-release versions should be included, False otherwise.

        Since:
            v3.0

        """
        return self.__include_pre_release_for_update_check

    @property
    def installed_newer_than_latest(self):
        return self.installed > self.latest_stable

    @include_pre_release_for_update_check.setter
    def include_pre_release_for_update_check(self, new):
        if isinstance(new, bool):
            self.__include_pre_release_for_update_check = new
        else:
            raise TypeError(f'Expected bool, received {type(new)}.')

    @property
    def installed(self):
        """
        Gets the installed version of the package.

        Returns:
            packaging.version.Version:
                The installed version of the package.

        """
        return pkg_version.parse(self.__installed)

    @property
    def latest_stable(self):
        """
        Gets the latest stable version of the package on PyPi.

        Returns:
            str: The latest stable version of the package on PyPi.

        Since:
            v3.0
        """
        if self.__latest_stable is not  None:
            return pkg_version.parse(self.__latest_stable)

        return self.__latest_stable

    @property
    def latest_pre_release(self):
        """
        Gets the latest pre-release version of the package.

        Returns:
            str: The latest pre-release version of the package.

        Since:
            v3.0
        """
        if self.all_versions is not None and self.__latest_pre_release is None:
            most_recent = pkg_version.parse(self.all_versions[-1])
            if most_recent.is_prerelease:
                self.__latest_pre_release = most_recent

        return self.__latest_pre_release

    @property
    def new_version_available_num(self):
        """
        Gets the number of the latest version available on PyPi.

        Returns:
            int: The number of the latest version available on PyPi.

        Since:
            v3.0
        """
        if not self.checked_for_update:
            self.update_available
        return self.__new_version_available_num

    @property
    def queried(self):
        """
        Checks if the versions have been queried.

        Returns:
            bool: True if the versions have been queried, False otherwise.

        Since:
            v3.0
        """
        return self.__queried

    @property
    def update_available(self):
        """
        Checks if an update is available.

        Returns:
            bool: True if an update is available, False otherwise.

        Since:
            v3.0
        """
        if not self.queried:
            #print('Querying versions')
            self.__query_versions()

        if not self.checked_for_update:
            #print('Checking for update')
            self.__compare_latest()
            self.__checked_for_update = True

        if self.new_version_available_num is None and not self.queried:
            #print('Getting latest')
            self.__compare_latest()

        return self.new_version_available_num is not None




    def __query_versions(self):
        """
        Queries the versions from PyPi.

        Returns:
            dict: The versions from PyPi.

        Since:
            v3.0
        """
        if not self.queried:
            resp = requests.get(self.__url)
            resp.raise_for_status()
            #print(resp.status_code)
            resp = resp.json()

            self.__all_versions = list(resp['releases'].keys())
            #print(self.all_versions)

            self.__latest_stable = resp['info']['version']
            #print(self.latest_stable)



            self.__queried = True

    def __compare_latest(self):
        latest = self.__get_latest()

        if latest is not None and latest > self.installed:
            self.__new_version_available_num = latest

    def __get_latest(self):
        if not self.queried:
            #print('Querying versions')
            self.__query_versions()

        return (
            self.latest_pre_release
            if self.include_pre_release_for_update_check
            else self.latest_stable
        )
