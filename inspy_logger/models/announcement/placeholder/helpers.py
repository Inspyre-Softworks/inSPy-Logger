import re
from typing import Optional
from inspy_logger.common import InspyLogger
from inspy_logger.models.announcement.placeholder import PlaceHolderString, PlaceHolderCollection


DEFAULT_DELIMITERS = {
        'open':  '{',
        'close': '}'

        }


def generate_placeholder_collection(
        template: str,
        owner: InspyLogger,
        open_delimiter: Optional[str] = DEFAULT_DELIMITERS['open'],
        close_delimiter: Optional[str] = DEFAULT_DELIMITERS['close']
        ) -> PlaceHolderCollection:
    """
    Generates a PlaceholderCollection based on a template string.

    Parameters:
        template (str):
            The template string containing placeholders.

        owner (Logger):
            The logger instance that owns the placeholders.

        open_delimiter (str):
            The opening delimiter for the placeholders. Defaults to '{'.

        close_delimiter (str):
            The closing delimiter for the placeholders. Defaults to '}'.

    Returns:
        PlaceHolderCollection:
            The generated :class:`PlaceholderCollection`.
    """
    placeholders = re.findall(rf'{re.escape(open_delimiter)}(.*?){re.escape(close_delimiter)}', template)
    return PlaceHolderCollection(
            owner = owner,
            template = template,
            open_delimiter=open_delimiter,
            close_delimiter=close_delimiter
            )
