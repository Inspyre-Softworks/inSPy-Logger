import contextlib
import requests
from packaging import version as pkg_version
import sys
from rich.table import Table
from rich import print
from typing import Optional, Literal
import re
from pathlib import Path


# Constants
RELEASE_MAP = {
    'dev': 'Development Build',
    'alpha': 'Alpha Build',
    'beta': 'Beta Build',
    'rc': 'Release Candidate Build',
    'final': 'Final Release Build'
}


def get_full_version_name():
    """
    Gets the full version name.

    Returns:
        str: The full version name.

    Since:
        v1.0
    """
    return VERSION_PARSER.to_full_version_string()


def parse_version():
    """
    Parses the version information into a string.

    Returns:
        str: The version information.

    Since:
        v1.0
    """
    return VERSION_PARSER.version_str


class VersionParser:
    def __init__(self, version_str):
        self.version_str = version_str
        self.version_info = self.parse_version()

    @staticmethod
    def get_release(release_type: Literal[tuple(RELEASE_MAP.keys())]) -> str:
        """
        Gets the release name from the release type.

        Parameters::
            release_type (str):
                The release type.

                Must be one of;
                  - 'dev'
                  - 'alpha'
                  - 'beta'
                  - 'rc' or;
                  - 'final'

        Returns:
            str:
                The full name of the release type.

        Raises:
            ValueError:
                If the release type is not one of the valid release types.

            TypeError:
                If the release type is not a string.

        Examples:
            >>> VersionParser.get_release('dev')
            'Development Build'

            >>> VersionParser.get_release('alpha')
            'Alpha Build'

            >>> VersionParser.get_release('beta')
            'Beta Build'

            >>> VersionParser.get_release('rc')
            'Release Candidate Build'

            >>> VersionParser.get_release('final')
            'Final Release Build'

        """
        if not isinstance(release_type, str):
            raise TypeError(f'Release type must be a string, not {type(release_type)}')

        release_type = release_type.lower()

        if release_type not in RELEASE_MAP:
            raise ValueError(f'Invalid release type: {release_type}. Must be one of {tuple(RELEASE_MAP.keys())}')

        return RELEASE_MAP.get(release_type)

    def parse_version(self):
        """
        Parses the version string into its components.

        Returns:
            dict: A dictionary containing the major, minor, patch, release, and release number.

        Raises:
            ValueError: If the version string format is grossly incorrect.
        """
        parts = self.version_str.split('-')
        version_numbers = parts[0].split('.')
        major, minor, patch = map(int, version_numbers)

        release = 'final'
        release_num = 0
        release_type = 'final'  # Default release type

        if len(parts) > 1:
            release_info = parts[1]
            release_info_parts = re.split(r'[\.\+]', release_info)
            release_type = release_info_parts[0]
            release = RELEASE_MAP.get(release_type, 'final')

            if len(release_info_parts) > 1 and release_info_parts[1].isdigit():
                release_num = int(release_info_parts[1])

        return {
            'major': major,
            'minor': minor,
            'patch': patch,
            'release': release,
            'release_abbr': release_type,
            'release_num': release_num
        }

    def to_full_version_string(self):
        """
        Constructs a full version string with the descriptive release name and number.

        Returns:
            str: The full version string in the format 'vX.Y.Z Release Type Release Num'.
        """

        major, minor, patch = self.version_info['major'], self.version_info['minor'], self.version_info['patch']
        release, release_num = self.version_info['release'], self.version_info['release_num']

        version_str = f"v{major}.{minor}.{patch}"
        if release != 'Final Release Build':
            version_str += f" {release}"
            if release_num > 0:
                version_str += f" {release_num}"

        return version_str

    def print_version(self, skip_rich=False):
        if not skip_rich:
            with contextlib.suppress(ImportError):
                self.__rich__()
                return
        self._print_version()

    def _print_version(self):
        version_info = self.version_info
        print(version_info)

    def __str__(self):
        return self.version_str

    def __repr__(self):
        return f"VersionParser('{self.version_str}\n')"

    def __rich__(self):
        from rich.table import Table
        from rich import box
        table = Table(box=box.SIMPLE)
        table.add_column('Major', justify='right', style='cyan')
        table.add_column('Minor', justify='right', style='magenta')
        table.add_column('Patch', justify='right', style='green')
        table.add_column('Release', justify='right', style='yellow')
        table.add_column('Release Num', justify='right', style='blue')
        table.add_row(str(self.version_info['major']), str(self.version_info['minor']), str(self.version_info['patch']),
                      self.version_info['release'], str(self.version_info['release_num']))
        return table

    @property
    def full_version_string(self):
        """
        Gets the full version string.

        Returns:
            str:
                The full version string.
        """
        return self.to_full_version_string()

    @property
    def major(self):
        return self.version_info['major']

    @property
    def minor(self):
        return self.version_info['minor']

    @property
    def patch(self):
        return self.version_info['patch']

    @property
    def release(self):
        return self.version_info['release']

    @property
    def release_num(self):
        return self.version_info['release_num']


def parse_version_file():
    with open(Path(__file__).parent.joinpath('VERSION.txt'), 'r') as f:
        return VersionParser(f.read().strip())


VERSION_PARSER = parse_version_file()


class PyPiVersionInfo:
    """
    A class to represent the version information for this package from PyPi.

    Attributes:
        newer_available_version (packaging.version.Version):
            The latest stable version of the package on PyPi.

        latest_pre_release (packaging.version.Version):
            The latest pre-release version of the package.
    Since:
        v3.0
    """
    __url = 'https://pypi.org/pypi/inspy-logger/json'
    __installed = parse_version()
    __checked_for_update = False
    __newer_available_version = None

    def __init__(self, include_pre_release_for_update_check=False):
        self.__latest_stable = None
        self.__latest_pre_release = None
        self.__all_versions = None
        self.include_pre_release_for_update_check = include_pre_release_for_update_check
        self.__query_versions()

    @property
    def all_versions(self):
        if self.__all_versions is None:
            self.__query_versions()
        return sorted([pkg_version.parse(v) for v in self.__all_versions])

    @property
    def checked_for_update(self):
        return self.__checked_for_update

    @property
    def installed(self):
        """
        Gets the installed version of the package.
        """
        return pkg_version.parse(self.__installed)

    @property
    def installed_newer_than_latest(self):
        return self.installed > self.latest

    @property
    def latest(self):
        return (
            self.all_versions[-1]
            if self.include_pre_release_for_update_check
            else self.latest_stable
        )

    @property
    def latest_stable(self):
        """
        Gets the latest stable version of the package on PyPi.
        """
        if self.__latest_stable is None:
            self.__query_versions()
        return pkg_version.parse(self.__latest_stable)

    @property
    def latest_pre_release(self):
        """
        Gets the latest pre-release version of the package.
        """
        if self.__all_versions is None:
            self.__query_versions()
        pre_release_versions = [v for v in self.all_versions if v.is_prerelease]
        return pre_release_versions[-1] if pre_release_versions else None

    @property
    def newer_available_version(self):

        if self.__newer_available_version is None:
            self.check_for_update()

        return self.__newer_available_version

    def __query_versions(self):
        """
        Queries the versions from PyPi.
        """
        try:
            response = requests.get(self.__url)
            response.raise_for_status()
            data = response.json()

            self.__all_versions = list(data['releases'].keys())
            self.__latest_stable = data['info']['version']
        except requests.RequestException as e:
            # Handle connection errors, HTTP errors, etc.
            print(f"Error querying PyPi: {e}")

    @property
    def update_available(self):
        """
        Checks if an update is available.
        """
        if self.__newer_available_version is None:
            self.check_for_update()
        return self.__newer_available_version is not None

    def check_for_update(self, include_pre_releases=False):
        latest_version = self.latest_stable

        if include_pre_releases or self.include_pre_release_for_update_check:
            latest_version = max(latest_version, self.latest_pre_release)

        if latest_version > self.installed:
            self.__newer_available_version = latest_version

        self.__checked_for_update = True

        return latest_version > self.installed

    def get_all_versions(self, include_pre_release: Optional[bool] = True):
        """
        Gets all versions of the package.

        Parameters:
            include_pre_release (bool, optional):
                A flag to include pre-release versions in the output. Defaults to True.

        Returns:
            list[pkg_version.Version]:
                A list of versions of the package.
        """
        return self.all_versions if include_pre_release else [v for v in self.all_versions if not v.is_prerelease]

    def update(self):
        """
        Checks for updates to inspy-logger.

        Returns:
            None`

        Since:
            v3.0
        """

        local_newer_statement = 'Local version is newer than latest version. This is likely a development build.'

        if not self.installed_newer_than_latest:
            local_newer_statement = ''

        try:
            if self.update_available:
                print(f'\n\n[bold green]Update Available![/bold green]\nNew version: '
                      f'[bold cyan]{self.update_available}[/bold cyan]')
            else:
                print(f'\n\n[bold green]No update available.[/bold green]\nCurrent version: '
                      f'[bold cyan]{parse_version()}[/bold cyan]\n{local_newer_statement}')

            print('\n')

        except Exception as e:
            print(f'An error occurred during the update check: {str(e)}')

    def __get_all_versions_table(self, versions: list[pkg_version.Version]):
        """
        Gets a table of versions.

        Parameters:
            versions (list[pkg_version.Version]):
                A list of versions to print.

        Returns:
            Table:
                A table of versions.
        """
        table = Table(show_header=False, show_lines=True, expand=True, border_style='bright_blue',
                      row_styles=['none', 'dim'])

        table.add_column('Version', style='cyan', width=20)

        for v in versions:
            table.add_row(str(v))

        return table

    def __get_all_versions_string(self, versions: list[pkg_version.Version]):
        """
        Gets a string of versions.

        Parameters:
            versions (list[pkg_version.Version]):
                A list of versions to print.

        Returns:
            str:
                A string of versions.
        """
        return ', '.join([str(v) for v in versions])

    def print_all_versions(
            self,
            include_pre_release: Optional[bool]  = True,
            print_table: Optional[bool] = True,
    ):
        """
        Prints all versions of the package.

        Parameters:
            include_pre_release (bool, optional):
                A flag to include pre-release versions in the output. Defaults to True.

            print_table (bool, optional):
                A flag to print the versions in a table. Defaults to True.

        Returns:
            None
        """
        # Collect the versions.
        versions = self.get_all_versions(include_pre_release)

        printable = self.__get_all_versions_string(versions) if not print_table else self.__get_all_versions_table(versions)

        print(printable)

    def print_version_info(self):
        """
        Print version information in a formatted table.

        This function creates a table using the `Table` class and populates it with version information about the current Python environment. It then prints the table to the console.

        Parameters:
            self: The current instance of the class.

        Returns:
            None
        """

        # Create a table

        table = Table(show_header=False, show_lines=True, expand=True, border_style='bright_blue',
                      row_styles=['none', 'dim'])

        # Add columns
        table.add_column('Property', style='cyan', width=20)
        table.add_column('Value', justify='center')

        # Add rows
        table.add_row('Version', parse_version(), )
        table.add_row('Full Version Name', get_full_version_name())

        if self.update_available:
            table.add_row('Update Available', '[bold green]Yes[/bold green]')
            table.add_row('Latest Version', f'{self.newer_available_version}')

        table.add_row('Python Executable Path', sys.executable)
        table.add_row('Python Version', sys.version)

        print(table)


if __name__ == '__main__':
    del VersionParser
