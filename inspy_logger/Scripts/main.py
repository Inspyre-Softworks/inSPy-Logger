"""

File: 
    inspy_logger/Scripts/main.py

Author: 
    Inspyre Softworks
    
"""
INSPY_LOG_LEVEL = 'info'

PROGNAME = 'inspy-logger-tool'

from argparse import ArgumentParser

from inspy_logger.helpers.debug.environment import fetch_system_info
from inspy_logger.version import parse_version, PyPiVersionInfo



# ---- SET UP PARSER --------------------------------
=======
from inspy_logger.version import parse_version, get_full_version_name, PyPiVersionInfo
import sys
from rich import print
from rich.table import Table
from argparse import ArgumentParser

# ---- SET UP SUBPARSERS --------------------------------

subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

# ---- UPDATE COMMAND --------------------------------

update_parser =subparsers.add_parser('update', help='Checks for updates to inspy-logger.')

update_parser.add_argument('-p', '--pre-release', action='store_true', help='When checking for updates, include pre-release versions.')

# ---- DEBUG COMMAND --------------------------------

debug_parser = subparsers.add_parser('debug', help='Fetches a collection of  environment information to help debug inspy-logger.')

debug_parser.add_argument('-C', '--copy-to-clipboard', action='store_true', help='Copies the debug information to the clipboard.')
debug_parser.add_argument('-P', '--print', action='store_true', help='Prints the debug information to the console.')

# ---- FORMAT FLAGS --------------------------------

fmt_grp = debug_parser.add_mutually_exclusive_group()

fmt_grp.add_argument('-M', '--markdown', action='store_true', help='Formats the debug information in Markdown.')

fmt_grp.add_argument('-J', '--json', action='store_true', help='Formats the debug information in JSON.')

fmt_grp.add_argument('-T', '--text', action='store_true', help='Formats the debug information in plain text.')

# Parse the arguments
parsed_args = parser.parse_args()

# END PARSER SETUP

if parsed_args.subcommand == 'update':
    INCLUDE_PRE_RELEASE_FOR_UPDATE_CHECK = parsed_args.pre_release
else:
    INCLUDE_PRE_RELEASE_FOR_UPDATE_CHECK = False


def debug(args = parsed_args):
    if args.markdown:
        fmt = 'markdown'
    elif args.json:
        fmt = 'json'
    else:
        fmt = 'text'

    fetch_system_info(copy_to_clipboard=args.copy_to_clipboard, format_type=fmt, print_to_console=args.print)



def main():

    version = PyPiVersionInfo(INCLUDE_PRE_RELEASE_FOR_UPDATE_CHECK)

    ACTIONS = {
        'default': version.print_version_info,
        'update': version.update,
        'debug': debug,

    }

    if parsed_args.subcommand is None:
        parsed_args.subcommand = 'default'

    # Run the action.
    ACTIONS[parsed_args.subcommand]()


if __name__ == '__main__':
    main()
