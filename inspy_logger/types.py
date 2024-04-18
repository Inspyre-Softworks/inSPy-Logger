"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/types.py
 

Description:
    

"""
from inspy_logger.constants import LEVEL_MAP
from inspy_logger.helpers import translate_to_logging_level
from inspy_logger.helpers.decorators import validate_type


class LogLevel:
    """
    A class for defining log levels for the logger.
    """
    LOG_LEVELS = {
        'DEBUG',
        'INFO',
        'WARNING',
        'ERROR',
        'CRITICAL',
    }

    __allowed_values = LOG_LEVELS

    __case_sensitive = None

    def __init__(self, log_level: str = 'INFO', case_sensitive=False):
        self.__level_name = None

        self.case_sensitive = case_sensitive

        levels = list(self.LOG_LEVELS)

        if isinstance(log_level, str):
            if not case_sensitive:
                for level in levels:
                    self.__allowed_values.add(level.lower())

        elif isinstance(log_level, int):
            self.level_name = self.from_int(log_level)

        self.level_name = log_level

    @property
    def allowed_values(self):
        return self.__allowed_values

    @property
    def case_sensitive(self):
        return self.__case_sensitive

    @case_sensitive.setter
    @validate_type(bool)
    def case_sensitive(self, case_sensitive: bool):
        self.__case_sensitive = case_sensitive

    @property
    def level_name(self):
        return self.__level_name

    @level_name.setter
    @validate_type(str, case_sensitive=False, allowed_values=LOG_LEVELS)
    def level_name(self, new_level: str):
        self.__level_name = new_level.upper()

    @classmethod
    def from_str(cls, level_string):
        level = level_string.upper()
        if level not in cls.LOG_LEVELS:
            raise ValueError(f"Invalid log level: {level_string}, must be one of {cls.LOG_LEVELS}")

        return cls(level)

    @classmethod
    def from_int(cls, level_integer):
        for level in cls.LOG_LEVELS:
            if translate_to_logging_level(level) == level_integer:
                return cls(level)

        raise ValueError(f"Invalid log level: {level_integer}, must be one of {cls.LOG_LEVELS}")

    def as_int(self):
        return translate_to_logging_level(self.level_name)

    def upper(self):
        return self.level_name.upper()

    def lower(self):
        return self.level_name.lower()

    def __str__(self):
        return self.level_name

    def __int__(self):
        return translate_to_logging_level(self.level_name)

    @classmethod
    def get_levels(cls):
        return [cls.DEBUG, cls.INFO, cls.WARNING, cls.ERROR, cls.CRITICAL]


class LogLevel(LogLevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __convert_if_needed(self, other):
        if not isinstance(other, LogLevel):
            if isinstance(other, str):
                other = self.from_str(other)
            elif isinstance(other, int):
                other = self.from_int(other)

        return other

    def __eq__(self, other):
        other = self.__convert_if_needed(other)
        return self.level_name == other.level_name

    def __hash__(self):
        return hash(self.level_name)

    def __le__(self, other):
        other = self.__convert_if_needed(other)
        return self.as_int() <= other.as_int()


    def __lt__(self, other):
        other = self.__convert_if_needed(other)

        return self.as_int() < other.as_int()


    def __ge__(self, other):
        other = self.__convert_if_needed(other)
        return self.as_int() >= other.as_int()


    def __gt__(self, other):
        other = self.__convert_if_needed(other)
        return self.as_int() > other.as_int()


    def __repr__(self):
        return f"LogLevel: {self.level_name} | {self.as_int()} at {hex(id(self))})"


def assemble_log_levels():
    _ = list(LogLevel.LOG_LEVELS)
    levels = [level for level in _ if level.isupper()]

    levels = sorted(levels, key=lambda x: LEVEL_MAP[x.lower()])

    return {LogLevel(level) for level in levels}


if 'LOG_LEVELS' not in globals():
    LOG_LEVELS = assemble_log_levels()
