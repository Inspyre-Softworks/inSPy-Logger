"""

File: 
    inspy_logger/Scripts/main.py

Author: 
    Inspyre Softworks
    
"""
INSPY_LOG_LEVEL = 'info'

from inspy_logger.version import parse_version, get_full_version_name, PyPiVersionInfo
import sys
from rich import print
from rich.table import Table
from argparse import ArgumentParser


parser = ArgumentParser('inspy-logger-version', description='Displays version information for inspy-logger.')

parser.add_argument('-v', '--version', action='version', version=parse_version())

subparsers = parser.add_subparsers(title='subcommands', dest='subcommand')

update_parser =subparsers.add_parser('update', help='Checks for updates to inspy-logger.')

update_parser.add_argument('-p', '--pre-release', action='store_true', help='When checking for updates, include pre-release versions.')

parsed_args = parser.parse_args()


if parsed_args.subcommand == 'update':
    INCLUDE_PRE_RELEASE_FOR_UPDATE_CHECK = parsed_args.pre_release
else:
    INCLUDE_PRE_RELEASE_FOR_UPDATE_CHECK = False


pypi_info = PyPiVersionInfo(include_pre_release_for_update_check=INCLUDE_PRE_RELEASE_FOR_UPDATE_CHECK)


def update():
    """
    Checks for updates to inspy-logger.

    Returns:
        None

    Since:
        v3.0
    """
    try:
        if pypi_info.update_available:
            print(f'\n\n[bold green]Update Available![/bold green] New version: [bold cyan]{pypi_info.new_version_available}[/bold cyan]')
        else:
            print(f'\n\n[bold green]No update available.[/bold green] Current version: [bold cyan]{parse_version()}[/bold cyan] {"which is newer than the available version on PyPi.org" if pypi_info.installed_newer_than_latest else ""}')
    except Exception as e:
        print(f'An error occurred during the update check: {str(e)}')


def get_version_info():
    # Create a table
    table = Table(show_header=False, show_lines=True, expand=True, border_style='bright_blue',
                  row_styles=['none', 'dim'])

    # Add columns
    table.add_column('Property', style='cyan', width=20)
    table.add_column('Value', justify='center')

    # Add rows
    table.add_row('Version', parse_version(), )
    table.add_row('Full Version Name', get_full_version_name())

    if pypi_info.update_available:
        table.add_row('Update Available', '[bold green]Yes[/bold green]')
        table.add_row('Latest Version', f'{pypi_info.new_version_available_num}')

    table.add_row('Python Executable Path', sys.executable)
    table.add_row('Python Version', sys.version)

    print(table)



def main():

    return update() if parsed_args.subcommand == 'update' else get_version_info()



if __name__ == '__main__':
    main()
