"""
:author: Inspyre-Softworks
:project: InSPy-Logger
:file: inspy_logger/models/announcement/placeholder/__init__.py

Description:
    This module defines the :class:`PlaceHolderString` class, which extends the built-in string type to include
    custom delimiters for placeholders, ensuring that certain conditions are met when setting the placeholders and
    delimiters.

"""
import re
import inspect
from inspy_logger.common import InspyLogger

from inspy_logger.helpers import translate_to_logging_level_str

from inspy_logger.helpers.decorators import validate_type

DEFAULT_DELIMITERS = {
        'open':  '{',
        'close': '}'
        }

DEFAULT_TEMPLATE = 'Initialized {name}'


class PlaceHolderString:
    DEFAULT_OPEN_DELIMITER = DEFAULT_DELIMITERS['open']
    DEFAULT_CLOSE_DELIMITER = DEFAULT_DELIMITERS['close']

    def __init__(
            self,
            placeholder: str,
            open_delimiter: str = DEFAULT_OPEN_DELIMITER,
            close_delimiter: str = DEFAULT_CLOSE_DELIMITER,
            value: str = None
            ) -> None:
        self.__placeholder = None
        self.__open = None
        self.__close = None
        self.__value = None

        self.open_delimiter = open_delimiter
        self.close_delimiter = close_delimiter

        self.placeholder = placeholder

        if value:
            self.value = value

    @property
    def close_delimiter(self) -> str:
        """
        The closing delimiter.
        """
        return self.__close

    @close_delimiter.setter
    @validate_type(str)
    def close_delimiter(self, value: str) -> None:
        """
        Set the closing delimiter.

        Parameters:
            value (str):
                The closing delimiter.

        Returns:
            None

        Raises:
            ValueError:
                If the closing delimiter is the same as the opening delimiter.

            TypeError:
                If the closing delimiter is not a string.

            ValueError:
                If the closing delimiter is in the placeholder.

            ValueError:
                If the closing delimiter has already been set.
        """
        if value == self.open_delimiter:
            raise ValueError('Open and close delimiters cannot be the same.')

        if self.placeholder and value in self.placeholder:
            raise ValueError('Close delimiter cannot be in placeholder.')

        if self.__close:
            raise ValueError('Close delimiter cannot be changed once set.')

        self.__close = value

    @property
    def open_delimiter(self) -> str:
        """
        The opening delimiter.
        """
        return self.__open

    @open_delimiter.setter
    @validate_type(str)
    def open_delimiter(self, value: str) -> None:
        """
        Set the opening delimiter.

        Parameters:
            value (str):
                The opening delimiter.

        Returns:
            None

        Raises:
            ValueError:
                If the opening delimiter is the same as the closing delimiter.

            TypeError:
                If the opening delimiter is not a string.

            ValueError:
                If the opening delimiter is in the placeholder.

            ValueError:
                If the opening delimiter has already been set.
        """
        if value == self.close_delimiter:
            raise ValueError('Open and close delimiters cannot be the same.')

        if self.placeholder and value in self.__placeholder:
            raise ValueError('Open delimiter cannot be in placeholder.')

        if self.__open:
            raise ValueError('Open delimiter cannot be changed once set.')

        self.__open = value

    @property
    def placeholder(self) -> str:
        """
        The placeholder string.
        """
        return self.__placeholder

    @placeholder.setter
    @validate_type(str)
    def placeholder(self, value: str) -> None:
        """
        Set the placeholder string.

        Parameters:
            value (str):
                The placeholder string.

        Returns:
            None

        Raises:
            ValueError:
                If the placeholder contains the :attr:`open` or :attr:`close` delimiters.

            ValueError:
                If the placeholder has already been set.

            TypeError:
                If the placeholder is not a string.
        """
        # Ensure the placeholder does not contain the delimiters.
        if self.open_delimiter in value or self.close_delimiter in value:
            raise ValueError('Placeholder cannot contain open or close delimiters.')

        # Ensure the placeholder has not already been set.
        if self.__placeholder:
            raise ValueError('Placeholder cannot be changed once set.')

        # Set the placeholder.
        self.__placeholder = value

    @property
    def value(self) -> str:
        """
        The value of the placeholder.
        """
        return self.__value

    @value.setter
    @validate_type(str)
    def value(self, new: str) -> None:
        """
        Set the value of the placeholder.

        Parameters:
            new (str):
                The new value of the placeholder.

        Returns:
            None
        """
        if self.value is not None:
            raise ValueError('Value cannot be changed once set.')

        self.__value = new

    def __str__(self) -> str:
        if not self.value:
            return f'{self.open_delimiter}{self.placeholder}{self.close_delimiter}'
        return self.value


class PlaceHolderCollection:
    DEFAULT_TEMPLATE = DEFAULT_TEMPLATE

    BUILTINS = [
            'name', 'console_level', 'file_level',
            'class_name', 'method_name', 'file_path',
            'time_started'
            ]

    def __init__(
            self,
            owner: InspyLogger = None,
            template: str = DEFAULT_TEMPLATE,
            placeholders: list[PlaceHolderString] = None,
            open_delimiter: str = PlaceHolderString.DEFAULT_OPEN_DELIMITER,
            close_delimiter: str = PlaceHolderString.DEFAULT_CLOSE_DELIMITER,
            skip_builtins: bool = False,
            ):
        """
        Initialize the placeholder collection.

        Parameters:
            owner Optional[InspyLogger]:
                The owner of the placeholders.

            template (str):
                The template string containing placeholders.

            open_delimiter (str):
                The opening delimiter for the placeholders. Defaults to '{'.

            close_delimiter (str):
                The closing delimiter for the placeholders. Defaults to '}'.
        """
        self.__owner = None
        self.__collected_from_template = False
        self.__template = None
        self.__placeholders = []
        self.__processed_builtins = []
        self.__open = None
        self.__close = None
        if owner is None:
            frame = inspect.currentframe()
            self.__owner = inspect.getmodule(frame.f_back)

        if template:
            self.template = template

        if [open_delimiter, close_delimiter] != [PlaceHolderString.DEFAULT_OPEN_DELIMITER,
                                                 PlaceHolderString.DEFAULT_CLOSE_DELIMITER] and (
                (open_delimiter == close_delimiter) or
                (open_delimiter in close_delimiter) or
                (close_delimiter in open_delimiter)
        ):
            raise ValueError('Invalid delimiters.')

        self.owner = owner

        if not skip_builtins:
            self.process_builtins()

        if template:
            _ = re.findall(
                    rf"{re.escape(open_delimiter)}(.*?){re.escape(close_delimiter)}",
                    template
                    )

        if placeholders:
            for placeholder in placeholders:
                if not skip_builtins and placeholder.placeholder in self.BUILTINS:
                    continue

    @property
    def builtin_placeholders(self):
        return self.__processed_builtins

    @property
    def close_delimiter(self):
        return self.__close

    @property
    def collected_from_template(self):
        return self.__collected_from_template

    @collected_from_template.setter
    @validate_type(bool)
    def collected_from_template(self, value: bool):
        if self.__collected_from_template:
            raise ValueError('Value cannot be changed once set.')

        self.__collected_from_template = value

    @property
    def filled_string(self):
        return self.template.format(**{ph.placeholder: ph.value for ph in self.placeholders})

    @property
    def open_delimiter(self):
        return self.__open

    @property
    def owner(self):
        return self.__owner

    @owner.setter
    @validate_type(InspyLogger)
    def owner(self, value: InspyLogger):
        self.__owner = value

    @property
    def placeholders(self) -> list[PlaceHolderString]:
        return self.__placeholders

    @property
    def template(self) -> str:
        return self.__template

    @template.setter
    @validate_type(str)
    def template(self, value: str) -> None:
        if self.__template:
            raise ValueError('Template cannot be changed once set.')
        self.__template = value

    def add(self, placeholder: PlaceHolderString) -> None:
        # Validate the placeholder.
        if not isinstance(placeholder, PlaceHolderString):
            raise ValueError('Invalid placeholder.')

        # Set the delimiters if they have not been set, otherwise validate the delimiters in the
        # incoming placeholder.
        if not self.placeholders:
            self.__open = placeholder.open_delimiter
            self.__close = placeholder.close_delimiter
        elif placeholder.open_delimiter != self.open_delimiter or placeholder.close_delimiter != self.close_delimiter:
            raise ValueError('Placeholder delimiters must match collection delimiters.')

        # Add the placeholder to the collection.
        self.__placeholders.append(placeholder)

    def collect_placeholders(self, template: str = template):
        if not self.collected_from_template:
            _ = re.findall(
                    rf'{re.escape(self.open_delimiter)}(.*?){re.escape(self.close_delimiter)}',
                    template,

                    )

    def process_builtins(self):
        if not self.owner:
            raise ValueError('Owner must be set to use built-in placeholders.')

        console_level = self.owner.console_level
        self.add(PlaceHolderString('name', value=self.owner.name))
        self.add(
                PlaceHolderString(
                        'console_level',
                        value=translate_to_logging_level_str(console_level)
                        )
                )

        self.add(
                PlaceHolderString(
                        'file_level',
                        value=translate_to_logging_level_str(self.owner.file_level)
                        )
                )

        self.add(
                PlaceHolderString(
                        'file_path',
                        value=str(self.owner.file_path)
                        )
                )

        self.add(
                PlaceHolderString(
                        'time_started',
                        value=str(self.owner.time_started)
                        )
                )

        if ':' in self.owner.name:
            class_name = self.owner.name.split(':')[0].split('.')[-1]
            method_name = self.owner.name.split(':')[-1]
            self.add(
                    PlaceHolderString(
                            'class_name',
                            value=class_name
                            )
                    )
            self.add(
                    PlaceHolderString(
                            'method_name',
                            value=method_name
                            )
                    )

    def __repr__(self):
        placeholders = ', '.join([str(ph) for ph in self.placeholders])
        return f'PlaceHolderCollection(owner={self.owner}, placeholders=[{placeholders}])'
