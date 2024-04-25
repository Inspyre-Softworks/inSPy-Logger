"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/common/meta/local_package.py
 

Description:
    

"""
from typing import List
from datetime import datetime
from packaging.version import parse as parse_version, Version
from inspy_logger.version import VERSION_PARSER
from inspy_logger.common.meta import constants as meta_constants
from inspy_logger.helpers import validate_type, RestrictedSetter
from inspy_logger.common.meta.helpers.data_classes import Release
from inspy_logger.common.meta.helpers.api import search_releases_for_version
from inspy_logger.helpers.decorators import add_aliases
from warnings import warn
from pathlib import Path



@add_aliases
class LocalPackageInfo:

    package_name = RestrictedSetter(
        'package_name',
        initial=meta_constants.PROG_NAME,
        allowed_types=str,
        restrict_setter=True
    )

    version = RestrictedSetter(
        'version',
        initial=str(VERSION_PARSER),
        allowed_types=str,
        restrict_setter=True
    )

    version_obj = RestrictedSetter(
        'version_obj',
        initial=parse_version(str(VERSION_PARSER)),
        allowed_types=Version,
        restrict_setter=True
    )

    release_date = RestrictedSetter(
        'release_date',
        initial=None,
        allowed_types=str,
        restrict_setter=True
    )

    release_obj = RestrictedSetter(
        'release_obj',
        initial=None,
        allowed_types=Release,
        restrict_setter=True,
    )

    dependencies = RestrictedSetter(
        'dependencies',
        initial=None,
        allowed_types=list,
        restrict_setter=True,
    )

    raw_info = RestrictedSetter(
        'raw_info',
        initial=None,
        allowed_types=dict,
        restrict_setter=True
    )

    __python_version = RestrictedSetter(
        '__python_version',
        initial=meta_constants.PYTHON_VERSION,
        allowed_types=str,
        restrict_setter=True
    )

    __local_package_path = meta_constants.LOCAL_PACKAGE_PATH

    def __init__(
            self,
            package_info: dict,
            package_name: str = meta_constants.PROG_NAME
    ):
        self.__version      = None
        self.__version_obj  = None
        self.__release_date = None
        self.__release_obj = None
        self.__dependencies = None

        self.raw_info = package_info

        self.package_name = package_name
        self.version = str(VERSION_PARSER)
        self.version_obj = parse_version(self.version)

        try:
            self.release_obj = search_releases_for_version(self.version, self.raw_info['release_objs'])[0]
        except IndexError:
            self.release_obj = None

        if not self.release_obj:
            latest_release_key = list(self.raw_info['releases'].keys())[-1]

            if self.version_obj > parse_version(latest_release_key):
                self.release_date = 'Future Release'
            else:
                self.release_date = 'Unknown'
                if len(self.raw_info['releases']) >= 1:
                    warn(f'No release data found for version {self.version}.')
                else:
                    warn('No release data found.')

            self.release_obj = self.create_release()

        else:
            self.release_date = self.release_obj[0].upload_time

        self.dependencies = self.raw_info['dependencies']

    release_date._alias_names = []
    package_name._alias_names = ['name']
    release_obj._alias_names = ['release', 'release_object']

    def create_release(self):
        return Release(self.version, self.release_date, [str(self.install_location)])

    def update_info(self):
        # Update the local package info
        # This is a placeholder, replace with actual code to update package info
        pass

    @property
    def dependency_name_list(self) -> List[str]:
        return [dep['name'] for dep in self.dependencies]

    @property
    def version_parser_obj(self):
        return VERSION_PARSER

    @property
    def full_version_string(self) -> str:
        return VERSION_PARSER.full_version_string

    @property
    def install_location(self) -> Path:
        return self.__local_package_path

    @property
    def python_version(self):
        if not self.__python_version:
            self.__python_version = f'{meta_constants.PYTHON_VERSION.major}.{meta_constants.PYTHON_VERSION.minor}'
        return self.__python_version

    @property
    def python_executable(self):
        return meta_constants.PYTHON_EXECUTABLE


print(__file__)
