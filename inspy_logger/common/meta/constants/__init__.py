"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/common/meta/constants.py
 

Description:
    

"""
from inspy_logger import initialized
from inspy_logger.system import SYSTEM_OS, get_executable_filepath, get_python_version, get_local_package_path


from inspy_logger.common.meta.constants import urls
from inspy_logger.common.meta.helpers import import_constants

__urls = {}

for constant in import_constants(urls):

    if 'URLS' not in globals():
        globals()['URLS'] = {}

    globals()['URLS'][constant.name] = constant.value


__all__ = [
    'AUTHORS',
    'LOCAL_PACKAGE_PATH',
    'PROG_NAME',
    'PYTHON_EXECUTABLE',
    'PYTHON_VERSION',
    'RELEASE_MAP',
    'SOFTWARE_ORG',
    'SOFTWARE_ORG_URL',
    'SYSTEM_OS',
    'URLS',
]

AUTHORS = [
    ('Inspyre-Softworks', URLS['DEVELOPER_URL']),
    ('Taylor-Jayde Blackstone', '<t.blackstone@inspyre.tech>')
]
"""The authors of the project."""

LOCAL_PACKAGE_PATH = get_local_package_path()

PROG_NAME = 'inSPy-Logger'
"""The name of the program."""

PYTHON_EXECUTABLE = get_executable_filepath()
"""The path to the Python executable."""

PYTHON_VERSION = get_python_version()
"""The version of Python."""

RELEASE_MAP = {
    'dev': 'Development Build',
    'alpha': 'Alpha Build',
    'beta': 'Beta Build',
    'rc': 'Release Candidate Build',
    'final': 'Final Release Build'
}
"""The release map for the project."""

SOFTWARE_ORG, SOFTWARE_ORG_URL = AUTHORS[0]
"""The organization that created the software, and the URL for that organization."""

URLS = dict(
    developer_url='https://inspyre.tech',
    docs_url='https://inspyre-toolbox.readthedocs.io/en/latest',
    github_url='https://github.com/tayjaybabee/Inspyre-Toolbox',
    pypi_url='https://pypi.org/project/inspyre-toolbox',
)
"""The URLs used in the project."""



if initialized:
    from inspy_logger.version import VERSION_PARSER

    VERSION = VERSION_PARSER

    __all__.append('VERSION')

# Delete the following objects as they are not needed in this module anymore.
del get_executable_filepath, get_python_version, get_local_package_path
