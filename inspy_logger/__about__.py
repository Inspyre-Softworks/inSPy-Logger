"""

File: inspy_logger/__about__.py
Project: inSPy-Logger
Description:
    Holds information about the inSPy-Logger program and its version.

Created: 11/3/22 - 21:05:06

Since:
    v2.1.1

"""

from inspy_logger.version import parse_version

__PROG__ = 'inSPy-Logger'
__VERSION__: str = parse_version()
__AUTHORS__: list[tuple[str, str]] = [
        ('Inspyre-Softworks', 'https://inspyre.tech'),
        ('Taylor-Jayde Blackstone', '<t.blackstone@inspyre.tech')
]

SOFTWARE_ORG = __AUTHORS__[0][0]
