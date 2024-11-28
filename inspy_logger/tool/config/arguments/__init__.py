from argparse import ArgumentParser
from inspy_logger.version import parse_version


class Arguments(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._subparsers = self.add_subparsers(title='subcommands', dest='subcommand')

        self._subparsers.add_argument()


parser = ArgumentParser('inspy-logger-version', description='Displays version information for inspy-logger.')

parser.add_argument('-v', '--version', action='version', version=parse_version())

# ---- SET UP SUBPARSERS --------------------------------

subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

# ---- UPDATE COMMAND --------------------------------

update_parser = subparsers.add_parser('update', help='Checks for updates to inspy-logger.')

update_parser.add_argument('-p', '--pre-release', action='store_true',
                           help='When checking for updates, include pre-release versions.')

# ---- DEBUG COMMAND --------------------------------

debug_parser = subparsers.add_parser('debug',
                                     help='Fetches a collection of  environment information to help debug inspy-logger.')

debug_parser.add_argument('-C', '--copy-to-clipboard', action='store_true',
                          help='Copies the debug information to the clipboard.')
debug_parser.add_argument('-P', '--print', action='store_true', help='Prints the debug information to the console.',
                          default=True)

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
