"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/common/meta/helpers/api.py
 

Description:
    

"""
from warnings import warn
from importlib_metadata import version as ilm_version, requires, distributions, PackageNotFoundError
from inspy_logger.constants import API_URL_BASE, API_SUFFIX
from typing import List
from dataclasses import dataclass
from datetime import datetime
from rich.console import Console
from rich.table import Table
from typing import Union
import site
import os
from packaging.requirements import Requirement
from packaging.version import parse as parse_version
from packaging.specifiers import SpecifierSet
from importlib_metadata import metadata
import requests
from requests.exceptions import HTTPError, ConnectionError
from inspy_logger.common.meta.helpers.data_classes import Release
from inspy_logger.common.meta.helpers.api.cache import cached_request, CacheEntry


@cached_request
def get_pypi_data(package_name: str, verify_status_code=True) -> dict:
    """
    Get package data from PyPI.

    Parameters:
        package_name (str):
            The name of the package to get data for.

        verify_status_code (bool):
            A flag to verify the status code of the response. Defaults to True.

    Returns:
        dict:
            The package data.
    """
    import requests

    url = f'{API_URL_BASE}{package_name}{API_SUFFIX}'
    response = requests.get(url)

    if verify_status_code:
        response.raise_for_status()

    return response.json()


def get_dependencies(package_name: str, fail_on_exception=False) -> List[dict]:
    """
    Get dependencies for a package.

    Parameters:
        package_name (str):
            The name of the package to get dependencies for.

    Returns:
        List[dict]:
            The dependencies for the package.
    """
    pkg_metadata = metadata(package_name)

    # Get the dependencies from the metadata.
    deps = pkg_metadata.get_all('Requires-Dist') or []

    dependencies = []

    for dep in deps:
        req = Requirement(dep)

        # Get the version range.
        version_range = str(req.specifier)

        # Get the installed version.
        installed_version = ilm_version(req.name)  # ilm_version is `version` imported from importlib_metadata.

        try:
            # Get the latest version within the range.
            # Get the package data from PyPI.
            data = get_pypi_data(req.name)

            # Get all the versions
            versions = [parse_version(v) for v in data.get('releases', {}).keys()]

            # Get the versions within the range.
            versions_within_range = [v for v in versions if v in SpecifierSet(version_range)]

            # Get the latest version within the range.
            latest_version_within_range = str(max(versions_within_range)) if versions_within_range else 'N/A'

        except Exception as e:
            if isinstance(e, KeyboardInterrupt) or fail_on_exception:
                raise e from e

            warn("Could not get data from PyPi on package, 'latest_version_within_range' will be incorrect!")

            latest_version_within_range = installed_version if parse_version(installed_version) in SpecifierSet(
                version_range) else 'N/A'

        # Add the dependency to the list.
        dependencies.append({
            'name': req.name,
            'version_range': version_range,
            'installed_version': installed_version,
            'latest_version_within_range': latest_version_within_range
        })

    return dependencies


def create_releases(data: dict, package_name: str, skip_pre_releases: bool = True) -> List[Release]:
    """
    Create a list of releases from package data.

    Parameters:
        data (dict):
            The package data.

        package_name (str):
            The name of the package to create releases for.

    Returns:
        List[Release]:
            A list of releases.
    """
    releases: List[Release] = []

    if isinstance(data, CacheEntry):
        data = data.data

    for version, uploads in data['releases'].items():
        parsed_ver = parse_version(version)

        if skip_pre_releases and parsed_ver.is_prerelease:
            continue

        upload_time = datetime.fromisoformat(uploads[0]['upload_time'])
        locations = get_package_install_locations(package_name)
        releases.append(Release(version, upload_time, locations))

    return releases


def get_package_install_locations(package_name: str) -> List[str]:
    """
    Get the installation locations for a package.

    Parameters:
        package_name (str):
            The name of the package to get the installation locations for.

    Returns:
        List[str]:
            The installation locations for the package.
    """
    locations = [p for p in site.getsitepackages() if os.path.isdir(os.path.join(p, package_name))]
    user_location = site.getusersitepackages() if os.path.isdir(
        os.path.join(site.getusersitepackages(), package_name)) else None

    if user_location:
        locations.append(user_location)

    return locations


def get_local_package_info(package_name: str = 'inspy-logger'):
    """
    Get the local package information.

    Parameters:
        package_name (str):
            The name of the package to get information for. Optional, defaults to 'inspy-logger'.

    Returns:
        dict:
            The local package information.
    """
    from inspy_logger.common.meta.local_package import LocalPackageInfo

    return LocalPackageInfo(package_name)


def get_package_info(
        package_name: str,
        include_pre_releases: bool = False,
        skip_releases: bool = False,
        skip_dependencies: bool = False,
        fail_on_exception: bool = False
) -> dict:
    """
    Get package information from PyPI.

    Parameters:
        package_name (str):
            The name of the package to get information for.

        include_pre_releases (bool):
            A flag to include pre-releases. Optional, defaults to False.

        skip_releases (bool):
            A flag to skip getting releases. Optional, defaults to False.

        skip_dependencies (bool):
            A flag to skip getting dependencies. Optional, defaults to False.

        fail_on_exception (bool):
            A flag to fail on exception. Optional, defaults to False.

    Returns:
        dict:
            The package information.
    """
    from inspy_logger.version import get_local_version

    data = {}

    if not skip_releases:
        try:
            # Get the package info.
            data = get_pypi_data(package_name)

            if isinstance(data, CacheEntry):
                data = data.data

        except Exception as e:
            if fail_on_exception:
                raise e from e
            warn(f'Failed to get package data for {package_name}.')

    if data:
        releases = create_releases(data, package_name, skip_pre_releases=not include_pre_releases)
    else:
        releases = []

    # Add releases to package info.
    data['release_objs']        = releases
    data['installed'] = {
        'version_info': {
            'version': get_local_version(),
            'version_obj': parse_version(get_local_version()),
            'release_date': ''
        }
    }
    data['version']             = get_local_version()
    data['version_obj']         = parse_version(data['version'])
    data['latest_is_installed'] = data['version_obj'] >= max(
        parse_version(r.version) for r in releases
    ) if releases else False

    if not skip_dependencies:
        try:
            # Get the dependencies for the package.
            data['dependencies'] = get_dependencies(package_name)
        except PackageNotFoundError as e:
            if fail_on_exception:
                raise e from e
            warn(f'Failed to get dependencies for {package_name}.')

    if 'dependencies' not in data:
        data['dependencies'] = []

    return data


def add_dependencies_to_table(table: Table, dependencies: List[dict]):
    """
    Add dependencies to a table.

    Parameters:
        table (Table):
            The table to add the dependencies to.

        dependencies (List[str]):
            The dependencies to add to the table.
    """
    # Add the given dependencies to the given table.
    for dependency in dependencies:
        table.add_row(
            dependency['name'],
            dependency['version_range'],
            dependency['installed_version'],
            dependency['latest_version_within_range']
        )


def add_releases_to_table(table: Table, releases: List[Release], skip_pre_releases=False):
    """
    Add releases to a table.

    Parameters:
        table (Table):
            The table to add the releases to.

        releases (List[Release]):
            The releases to add to the table.
    """
    # Add the given releases to the given table.
    for release in releases:
        parsed = parse_version(release.version)
        if skip_pre_releases and parsed.is_prerelease:
            continue
        else:
            table.add_row(release.version, str(release.upload_time), ', '.join(release.locations))


def print_package_info(
        package_name: str,
        skip_rich=False,
        skip_releases=False,
        skip_dependencies=False,
        return_data=False,
        include_pre_releases: bool = False) -> Union[dict, None]:
    """
    Print package information from PyPI.

    Parameters:
        package_name (str):
            The name of the package to get information for.

        skip_rich (bool):
            A flag to skip rich output. Optional, defaults to False.

        return_data (bool):
            A flag to return the package data. Optional, defaults to False.

        skip_releases (bool):
            A flag to skip releases. Optional, defaults to False.

        skip_dependencies (bool):
            A flag to skip dependencies. Optional, defaults to False.

        include_pre_releases (bool):
            A flag to include pre-releases. Optional, defaults to False.

    Returns:
        Union[dict, None]:
            The package information if `return_data` is True, otherwise None.
    """
    # Get the package info.
    package_info = get_package_info(package_name, include_pre_releases=include_pre_releases, skip_releases=skip_releases, skip_dependencies=skip_dependencies)

    if not skip_dependencies:
        # Add dependencies to the package info.
        package_info['dependencies'] = get_dependencies(package_name)

    # If `skip_rich` is False, print a rich table, otherwise print the package info.
    if not skip_rich:
        print_rich_tables(package_info, )
    else:
        print(package_info)

    # Return the package info if `return_data` is True.
    if return_data:
        return package_info


def create_release_table() -> Table:
    """
    Create a rich table.

    Returns:
        Table:
            The created table.
    """
    # Create a table.
    table = Table(title='Releases', show_header=True, header_style='bold yellow', highlight=True)

    # Add columns to the table.
    table.add_column('Version', style='dim', width=12)
    table.add_column('Upload Time', style='dim', width=20)
    table.add_column('Locations', style='dim', width=40)

    return table


def create_dependency_table() -> Table:
    """
    Create a table for dependencies.

    Returns:
        Table:
            The created table.
    """
    # Create a table.
    table = Table(title='Dependencies', show_header=True, header_style='bold yellow', highlight=True, show_lines=True)

    # Add columns to the table.
    table.add_column('Name', style='dim', width=20)
    table.add_column('Version Range', style='dim', width=20)
    table.add_column('Installed Version', style='dim', width=20)
    table.add_column('Latest Version Within Range', style='dim', width=20)

    return table


def print_package_description(package_name: str, skip_rich=False):
    """
    Print the description of a package.

    Parameters:
        package_name (str):
            The name of the package to print the description for.

        skip_rich (bool):
            A flag to skip rich output. Optional, defaults to False.

    Returns:
        None
    """
    try:
        # Get the package data.
        data = get_pypi_data(package_name)

        # Get the description.
        description = data['info']['description']

        if skip_rich:

            # Print the description.
            print(description)
        else:
            # Create a console.
            console = Console()

            # Print the description.
            console.print(description)
    except Exception as e:
        warn(f'Failed to get description for {package_name}.')


def build_release_table(releases: List[Release], skip_pre_releases=False) -> Table:
    """
    Build a rich table of releases.

    Parameters:
        releases (List[Release]):
            The releases to build the table for.

        skip_pre_releases (bool):
            A flag to skip pre-releases. Optional, defaults to False.

    Returns:
        Table:
            The built table.
    """
    # Create a table.
    table = create_release_table()

    # Add the releases to the table.
    add_releases_to_table(table, releases, skip_pre_releases=skip_pre_releases)

    return table


def print_tables(tables: List[Table]):
    """
    Print a rich table of releases.

    Parameters:
        tables (List(Table)):
            The table(s) to print.

    Returns:
        None
    """
    # Check if the tables are valid.
    # If the tables are not a list, tuple, or Table, raise a TypeError.
    if not isinstance(tables, (tuple, List, Table)):
        raise TypeError('`tables` must be a list (or tuple) of tables or a single table.')

    # If the tables are a tuple, convert them to a list.
    if isinstance(tables, tuple):
        tables = list(tables)

    # If the tables are a single table, convert it to a list.
    if isinstance(tables, Table):
        tables = [tables]

    # Create a console.
    console = Console()

    # Print the tables.
    for table in tables:
        console.print(table)


def build_dependency_table(dependencies: List[dict]) -> Table:
    """
    Build a rich table of dependencies.

    Parameters:
        dependencies (List[dict]):
            The dependencies to build the table for.

    Returns:
        Table:
            The built table.
    """
    # Create a table.
    table = create_dependency_table()

    # Add the dependencies to the table.
    add_dependencies_to_table(table, dependencies)

    return table


def print_rich_tables(
        package_info: dict,
        skip_releases: bool = False,
        skip_dependencies: bool = False,
):
    """
    Print a rich table of package information.

    Parameters:
        package_info (dict):
              The package information to print.

        skip_releases (bool):
            A flag to skip releases. Optional, defaults to False.

        skip_dependencies (bool):
            A flag to skip dependencies. Optional, defaults to False.

    Returns:
        None
    """
    tables = []

    if not skip_releases:
        # Create a table for releases.
        table = build_release_table(package_info['release_objs'])

        # Add the table to the tables list.
        tables.append(table)

    if not skip_dependencies:
        # Create a table for dependencies.
        table2 = build_dependency_table(package_info['dependencies'])

        # Add the table to the tables list.
        tables.append(table2)

    # Print the tables.
    print_tables(tables)


def search_releases_for_version(version, releases=None):
    if releases is None:
        releases = get_package_info('inspy-logger')['release_objs']

    return [r for r in releases if r.version == version]
