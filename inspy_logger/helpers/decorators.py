"""


Author:
    Inspyre Softworks

Project:
    inSPy-Logger

File:
    inspy_logger/helpers/decorators.py


Description:
    Contains decorators used by the inSPy-Logger package.

"""
from functools import wraps
from typing import Callable, Optional


__all__ = [
    'method_alias',
    'method_logger',
    'add_aliases',
    'count_invocations',
    'validate_type'
]


def property_logging(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.creating_logger:
            return
        if found := self.class_logger.find_child_by_name(func.__name__, exact_match=True):
            log = found
        else:
            self.creating_logger = True
            log = self.class_logger.add_child(func.__name__)
            self.creating_logger = False

        log.debug(f'Getting {func.__name__} from instance of {self.__class__.__name__}...', stack_level=4)
        res = func(self, *args, **kwargs)
        log.debug(f'Got {func.__name__} from instance of {self.__class__.__name__}: {res}', stack_level=4)

        return res
    return wrapper



def method_alias(*alias_names: (str, list[str])):
    """
    A decorator that allows you to add aliases to a class's method.

    Parameters:
        *alias_names (str, list[str]):
            The name(s) of the alias(es) to add.

    Returns:
        method:
            The decorated method.
    """
    def method_decorator(meth):
        meth._alias_names = alias_names
        return meth

    return method_decorator


def method_logger(func):
    """
    A decorator to log a method's execution.

    Parameters:
        func (method):
            The method to log.

    Returns:
        method:
            The decorated method.
    """
    def wrapper(self, *args, **kwargs):
        # Set up the logger with method-specific config.
        name = f'{self.__class__.__name__}.{func.__name__}'
        logger = self.class_logger.get_child()

        # Add the logger to the instance for use in the method
        self._current_logger = logger

        # Execute the called method
        res = func(self, *args, **kwargs)

        # Remove the logger after method execution
        del self._current_logger

        return res
    return wrapper


def add_aliases(cls):
    """
    A decorator to add aliases to a class's methods.

    Parameters:
        cls (class):
            The class to add aliases to.

    Returns:
        class:
            The decorated class.
    """
    for name, method in list(cls.__dict__.items()):
        if hasattr(method, '_alias_names'):
            for alias_name in method._alias_names:
                setattr(cls, alias_name, method)
    return cls


def count_invocations(method):
    """
    Decorator that counts the number of invocations of the method it decorates.

    Parameters:
        method (Callable):
            The method to count invocations for.

    Returns:
        Callable:
            The decorated method.
    """
    def wrapper(self, *args, **kwargs):
        method_name = method.__name__
        if method_name not in self.call_counts:
            self.call_counts[method_name] = 0

        self.call_counts[method_name] += 1

        return method(self, *args, **kwargs)

    return wrapper


def validate_type(
        *allowed_types,
        preferred_type=None,
        allowed_values=None,
        case_sensitive=True,
        conversion_funcs: Optional[dict] = None):
    """
    A decorator for validating the type and optionally the value of a value passed to a class
    property setter, with an option to convert to a preferred type if specified and to enforce
    value restrictions.

    Parameters:
        preferred_type (type, optional):
            The preferred type to which values should be converted if possible. If None, no
            conversion is attempted.

        *allowed_types:
            Variable length list of allowed types for the property value.

        allowed_values (iterable, optional):
            An iterable of values that are allowed. If None, all values of the correct type are allowed.

        case_sensitive (bool, optional):
            Specifies whether string comparisons should be case-sensitive. Defaults to True. Ignored for non-string
            types.

        conversion_funcs (dict, optional):
            A dictionary of conversion functions to use for converting

    Returns:
        A decorator function for the property setter.

    Raises:
        TypeError:
            If the incoming value does not match one of the allowed types, cannot be onverted to the preferred type,
            or is not in the list of allowed values.

        ValueError:
            If the value is of the correct type but not in the allowed values list.

    Example:
        >>> class MyClass:
        ...     @property
        ...     def my_property(self):
        ...         return self._my_property
        ...
        ...     @my_property.setter
        ...     @validate_type(str, allowed_values=["hello", "world"], case_sensitive=False)
        ...     def my_property(self, value):
        ...         self._my_property = value
        ...
        >>> obj = MyClass()
        >>> obj.my_property = "HELLO"  # This is accepted and set
        >>> obj.my_property = "hello"  # This is also accepted and set
        >>> obj.my_property = "Hi"  # This raises ValueError
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, value):
            if not isinstance(value, tuple(allowed_types)):
                allowed = ', '.join([t.__name__ for t in allowed_types])
                raise TypeError(f"Value must be of type {allowed}, got type {type(value).__name__}")

            if preferred_type and not isinstance(value, preferred_type):
                try:
                    if conversion_funcs and type(value) in conversion_funcs:
                        value = conversion_funcs[type(value)](value)
                    else:
                        value = preferred_type(value)
                except Exception as e:
                    raise TypeError(f"Could not convert value to preferred type {preferred_type.__name__}: {e}")

            if allowed_values is not None:
                if isinstance(value, str) and not case_sensitive:
                    validation_passed = any(val.lower() == value.lower() for val in allowed_values)
                else:
                    validation_passed = value in allowed_values

                if not validation_passed:
                    allowed_vals = ', '.join(map(str, allowed_values))
                    raise ValueError(f"Value must be one of {allowed_vals}, got {value}")

            return func(self, value)

        return wrapper

    return decorator


def validate_func_args(*validators):
    """
    A decorator for validating the type and optionally the value of arguments passed to a function.
    Each argument can have its own set of allowed types, a preferred type, and allowed values.

    Parameters:
        *validators (dict): Each dictionary in validators specifies the validation rules for one argument.
                            The keys in the dictionary can be:
                            - 'allowed_types': A tuple of allowed types for the argument.
                            - 'preferred_type': The preferred type to which the argument should be converted if possible.
                            - 'allowed_values': A list of values that the argument is allowed to have.
                            - 'case_sensitive': Specifies whether string comparisons should be case sensitive.

    Returns:
        A decorator function for the function.

    Raises:
        TypeError: If an argument does not match one of the allowed types or cannot be converted to the preferred type.
        ValueError: If the argument is of the correct type but not in the allowed values list.

    Example:
        >>> @validate_func_args(
        ...     {'allowed_types': (str,), 'allowed_values': ["hello", "world"], 'case_sensitive': False},
        ...     {'allowed_types': (int,), 'preferred_type': float}
        ... )
        ... def my_function(word, number):
        ...     print(f"{word} {number}")
        ...
        >>> my_function("HELLO", 123)  # This is valid and prints 'hello 123.0'
        >>> my_function("unknown", 123)  # This raises ValueError for the first argument
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            new_args = []
            for i, (arg, validator) in enumerate(zip(args, validators)):
                allowed_types = validator.get('allowed_types', ())
                preferred_type = validator.get('preferred_type')
                allowed_values = validator.get('allowed_values')
                case_sensitive = validator.get('case_sensitive', True)

                if not isinstance(arg, allowed_types):
                    allowed = ', '.join([t.__name__ for t in allowed_types])
                    raise TypeError(f"Argument {i} must be of type {allowed}, got type {type(arg).__name__}")

                if preferred_type and not isinstance(arg, preferred_type):
                    try:
                        arg = preferred_type(arg)
                    except Exception as e:
                        raise TypeError(
                            f"Could not convert argument {i} to preferred type {preferred_type.__name__}: {e}")

                if allowed_values is not None:
                    if isinstance(arg, str) and not case_sensitive:
                        validation_passed = any(val.lower() == arg.lower() for val in allowed_values)
                    else:
                        validation_passed = arg in allowed_values

                    if not validation_passed:
                        allowed_vals = ', '.join(map(str, allowed_values))
                        raise ValueError(f"Argument {i} must be one of {allowed_vals}, got {arg}")

                new_args.append(arg)

            return func(*new_args, **kwargs)

        return wrapper

    return decorator
