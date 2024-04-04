from platformdirs import user_log_path
from pathlib import Path
from inspy_logger.common.meta import *
from inspy_logger.helpers import (
    find_valid_vars_in_call_stack,
    VALID_LOG_FILE_VARS,
    VALID_PROG_NAME_VARS,
    determine_log_file_path,
    determine_client_prog_name,
    VALID_DEV_NAME_VARS
)

from typing import Optional, Union


INSPY_LOGGER_LOG_DIR_PATH = user_log_path(
    appname=PROG_NAME or find_valid_vars_in_call_stack(VALID_PROG_NAME_VARS),
    appauthor=SOFTWARE_ORG,
    ensure_exists=True
)

INSPY_LOGGER_LOG_FILE_NAME = 'app.log'

INSPY_LOGGER_LOG_FILE_PATH = INSPY_LOGGER_LOG_DIR_PATH.joinpath(INSPY_LOGGER_LOG_FILE_NAME)


# def get_log_file_path(
#         log_file_path: Union[str, Path] = None,
#         prog_name: str = None,
#         dev_name: str = None
# ) -> Path:
#     """
#     Get the path to the log file.
#
#     Parameters:
#         log_file_path (str, Path, optional):
#                The path to the log file.
#
#         prog_name (str):
#             The name of the program to be logged.
#
#         dev_name (str):
#             The name of the developer of the app to be logged.
#
#     Note:
#         The `log_file_name` is simply the name of the file to be logged to, not the full path.
#
#     Returns:
#         Path:
#             The path to the log file.
#     """
#     print(f'Found log-file path: {FOUND_LOG_FILE_VARS}')
#     log_file_path = log_file_path or FOUND_LOG_FILE_VARS
#     log_file_path = Path(log_file_path) if log_file_path else None
#
#     if not log_file_path:
#         if not prog_name:
#             prog_name = determine_client_prog_name()
#             print(f'Found prog-name: {prog_name}')
#         if prog_name and not dev_name:
#             dev_name = find_valid_vars_in_call_stack(VALID_DEV_NAME_VARS.valid_vars)
#
#             if dev_name:
#                 print(f'Found dev-name: {dev_name}')
#
#
#
#
#     #if not log_file_path.suffix and log_file_path.is_dir() and INSPY_LOGGER_LOG_FILE_NAME:
#     #    log_file_path = log_file_path.joinpath(INSPY_LOGGER_LOG_FILE_NAME)
#
#     if all(arg is None for arg in [
#         log_file_path,
#         prog_name,
#         dev_name
#     ]):
#         return INSPY_LOGGER_LOG_FILE_PATH
#
#     return log_file_path


def get_log_file_path(
        log_file_path: Union[str, Path] = None,
        prog_name: str = None,
        dev_name: str = None
) -> Path:
    """
    Get the path to the log file.

    Parameters:
        log_file_path (str, Path, optional):
               The path to the log file.

        prog_name (str):
            The name of the program to be logged.

        dev_name (str):
            The name of the developer of the app to be logged.

    Note:
        The `log_file_name` is simply the name of the file to be logged to, not the full path.

    Returns:
        Path:
            The path to the log file.
    """
    log_file_path = Path(log_file_path) if isinstance(log_file_path, str) else log_file_path

    if log_file_path:
        return log_file_path

    log_file_path = find_valid_vars_in_call_stack(VALID_LOG_FILE_VARS)

    if log_file_path:
        log_file_path = Path(log_file_path)
        return log_file_path

    if not prog_name:
        prog_name = determine_client_prog_name()

    if not dev_name and prog_name:
        dev_name = find_valid_vars_in_call_stack(VALID_DEV_NAME_VARS.valid_vars)

    if prog_name:
        file_name = f"{prog_name}.log"
        if dev_name:
            log_file_path = Path(user_log_path(appname=prog_name, appauthor=dev_name, ensure_exists=True)).joinpath(file_name)
        else:
            log_file_path = INSPY_LOGGER_LOG_DIR_PATH.joinpath(file_name)

    return log_file_path or INSPY_LOGGER_LOG_FILE_PATH


DEFAULT_LOG_FILE_PATH = get_log_file_path()
