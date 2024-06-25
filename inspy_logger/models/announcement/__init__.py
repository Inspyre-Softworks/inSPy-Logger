from typing import Optional, Union
from inspy_logger.common import InspyLogger, LEVEL_NAMES
from inspy_logger.helpers import translate_to_logging_level_str
from inspy_logger.helpers.decorators import validate_type
from inspy_logger.helpers.descriptors import RestrictedSetter
from inspy_logger.models.announcement.placeholder import PlaceHolderString, PlaceHolderCollection
from inspy_logger.models.announcement.placeholder.helpers import generate_placeholder_collection

from warnings import warn


class Announcement:

    DEFAULT_INITIALIZATION_ANNOUNCEMENT = 'Initialized {name}.'

    def __init__(self,
                 owner: InspyLogger,
                 template: Optional[str] = None,
                 announcement_level: Optional[Union[int, str]] = None
                 ):

        self.__owner = None
        self.__template = None
        self.__replacement_map = None
        self.__placeholders = None
        self.__announced = False
        self.__announcement_text = None
        self.__announcement_level = None
        self.__replaced = False

        self.announcement_text = RestrictedSetter('announcement_text', allowed_types=str, restrict_setter=True)
        if announcement_level is not None:
            self.announcement_level = announcement_level
        else:
            self.announcement_level = 'debug'

        self.owner = owner
        self.template = template
        self.placeholders = generate_placeholder_collection(self.template, self.owner)

    @property
    def announced(self) -> bool:
        return self.__announced

    @announced.setter
    @validate_type(bool)
    def announced(self, new: bool) -> None:
        """
        Set the announcement status.

        Parameters:
            new (bool):
                The announcement status.

        Returns:
            None

        Raises:
            ValueError:
                If the announcement has already been announced.
        """
        if not self.announced and new:
            self.__announced = new

        else:
            warn('Announcement has already been announced. Property `announced` remains unchanged!')

    @property
    def announcement_level(self):
        return self.__announcement_level

    @announcement_level.setter
    @validate_type(int, str, None, preferred_type=str, conversion_funcs={int: translate_to_logging_level_str})
    def announcement_level(self, new: str):
        """
        Set the logging level for the announcement.

        Parameters:
            new (Union[str, int]):
                The logging level for the announcement.

        Returns:
            None

        Raises:
            ValueError:
                If the logging level is invalid.
        """
        if self.announced:
            warn('Announcement has already been announced. Property `announcement_level` remains unchanged!')

        elif new.upper() not in LEVEL_NAMES:
            raise ValueError(f'Invalid logging level: {new}')

        else:
            self.__announcement_level = new

    @property
    def announcement_text(self) -> str:
        if self.__announcement_text is None:
            raise ValueError('Announcement text has not been set. Try calling `replace_placeholders()` first.')

        return self.__announcement_text

    @announcement_text.setter
    def announcement_text(self, value: str) -> None:
        self.__announcement_text = value

    @property
    def level(self):
        return self.announcement_level

    @property
    def owner(self) -> InspyLogger:
        """
        The owner of the announcement.
        """
        return self.__owner

    @owner.setter
    @validate_type(InspyLogger)
    def owner(self, value: InspyLogger) -> None:
        """
        Set the owner of the announcement.

        Parameters:
            value (InspyLogger):
                The owner of the announcement.

        Returns:
            None
        """
        self.__owner = value

    @property
    def replaced(self) -> bool:
        return self.__replaced

    @replaced.setter
    @validate_type(bool)
    def replaced(self, new: bool) -> None:
        self.__replaced = new

    @property
    def template(self) -> str:
        return self.__template

    @template.setter
    @validate_type(str)
    def template(self, new) -> None:
        self.__template = new

    def announce(self):
        """
        Announce the announcement.
        """
        self.replace_placeholders()
        if self.announced:
            warn('Announcement has already been announced. Skipping announcement.')
            return

        if hasattr(self.owner, self.level.lower()):
            getattr(self.owner, self.level.lower())(str(self))
        else:
            self.owner.warning(f'Invalid logging level: {self.level}')
            self.owner.debug(str(self))

        self.announced = True


    def replace_placeholders(self):
        if not self.replaced:
            self.announcement_text = self.placeholders.filled_string
            self.replaced = True

    def __str__(self):

        return self.placeholders.filled_string
