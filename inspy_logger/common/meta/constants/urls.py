"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/common/meta/urls.py
 

Description:
    This module contains the URL constants for the project.

"""

PROJECT_URL   = 'https://github.com/Inspyre-Softworks/inSPy-Logger'
GITHUB_URL    = PROJECT_URL
DEVELOPER_URL = 'https://inspyre.tech/'
ISSUES_URL    = f'{GITHUB_URL}/issues'
NEW_ISSUE_URL = F'{ISSUES_URL}/new?assignees=tayjaybabee&labels=Bug%3A%3AUnconfirmed&projects=&template=bug_report.md&title=%5BBUG%5D+It+ain%27t+working%21'
PYPI_URL      = 'https://pypi.org/project/inSPy-Logger'
RELEASES_URLS = {
    'pypi':   f'{PYPI_URL}/#history',
    'github': f'{GITHUB_URL}/releases'
}

DOCS_URL = 'https://inSPy-Logger.readthedocs.io/en/latest'


__all__ = [
    'DEVELOPER_URL',
    'DOCS_URL',
    'GITHUB_URL',
    'ISSUES_URL',
    'NEW_ISSUE_URL',
    'PROJECT_URL',
    'PYPI_URL',
    'RELEASES_URLS'
]
