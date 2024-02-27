from argparse import ArgumentParser
from inspy_logger.common import DEFAULT_LOGGING_LEVEL, LEVELS


def add_argument(parser: ArgumentParser, default=DEFAULT_LOGGING_LEVEL):
    """
    Add an argument to the given ArgumentParser object.

    Parameters:
        parser (ArgumentParser): The ArgumentParser object to add the argument to.
        default (Any): The default value for the argument. Defaults to DEFAULT_LOGGING_LEVEL.

    Returns:
       None

    Raises:
        None

    Description:
        This function adds an argument to the given ArgumentParser object. The argument is used to set the level at which to output logs to the console. The argument can be set using the '-l' or '--log-level' flags. The default value for the argument is set to DEFAULT_LOGGING_LEVEL. The valid choices for the argument are defined in the LEVELS variable.
    """
    parser.add_argument(
        '-l', '--log-level',
        action='store',
        default=default,
        choices=LEVELS,
        help='Set the level at which to output logs to the console.'
    )
