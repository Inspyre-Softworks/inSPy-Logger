import inspect
from inspy_logger import LOG_DEVICE, Logger


def _determine_calling_method(instance):
    """
    Attempt to determine the name of the method calling through `instance`.
    This function inspects the call stack for a frame where `self` is `instance`.
    Returns:
        str: The method name (string) of the calling method.
    Raises:
        RuntimeError: If no calling method can be identified.
    """
    stack = inspect.stack()
    # Start from 1 to skip the current frame
    for frame_record in stack[1:]:
        if frame_record.frame.f_locals.get('self') is instance:
            return frame_record.function
    raise RuntimeError("Could not determine the calling method's name.")


def _get_parent_logging_device():
    """
    Determines the parent logging device by inspecting the caller's local variables.
    It checks for 'logger' and 'parent_log_device' in the caller's locals. If found,
    returns it as the parent logger.

    Returns:
        Logger: The parent logging device.

    Raises:
        ValueError: If neither 'logger' nor 'parent_log_device' is found in the caller's locals.
    """
    LOG_DEVICE.debug("Determining parent logging device")

    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals

    if "logger" in caller_locals:
        return caller_locals["logger"]
    elif "parent_log_device" in caller_locals:
        return caller_locals["parent_log_device"]
    else:
        raise ValueError(
            "Unable to determine the parent logging device. "
            "Expected either 'logger' or 'parent_log_device' in caller's locals."
        )


class LoggableDescriptor:
    """
    A descriptor that, when accessed from an instance of a class inheriting from 'Loggable',
    returns a logger specific to the calling method.

    This relies on the instance having a 'create_logger' method and a class-level 'class_logger'.
    """

    def __get__(self, instance, owner):
        if instance is None:
            # Accessing through the class, return class-level logger
            return owner.class_logger

        method_name = _determine_calling_method(instance)
        # Get a child logger named after the class and method
        return instance.create_logger(name=method_name, is_method=True)


class Loggable:
    """
    A base class that provides logging capabilities to classes that inherit from it.

    It obtains a parent logger (either from a given parent_log_device or by introspection)
    and sets up a class-level logger. Instances can create method-specific or child loggers
    easily.

    Attributes:
        parent_log_device (Logger, optional): A parent logging device used to initialize this logger.
        class_logger (Logger, class-level): A class-level logger shared across all instances.
    """
    method_logger = LoggableDescriptor()
    class_logger = None

    def __init__(self, parent_log_device=None, **kwargs):
        """
        Initialize the Loggable instance.

        Parameters:
            parent_log_device (Logger, optional): The parent log device, if available.
            **kwargs: Additional keyword arguments.

        The instance-level logger is derived either from the given parent_log_device or by
        using _get_parent_logging_device(). The class-level logger is also set if not already done.
        """
        self.parent_log_device = parent_log_device
        self.__log_name = self.__class__.__name__

        if self.parent_log_device is not None:
            self.__log_device = self.parent_log_device.get_child(self.__log_name)
        else:
            self.__log_device = _get_parent_logging_device().get_child(self.__log_name)

        # Set up class-level logger if it's not already set
        if self.__class__.class_logger is None:
            self.__class__.class_logger = self.__log_device

    @property
    def log_device(self):
        """Return the instance's log_device."""
        return self.__log_device

    @log_device.setter
    def log_device(self, new):
        """Set a new logger device."""
        if not isinstance(new, Logger):
            raise TypeError('log_device must be of type "Logger"')
        self.__log_device = new

    def create_child_logger(self, name=None, override=False, is_method=False, **kwargs):
        """
        Create and return a child logger of this instance's logger.

        Parameters:
            name (str, optional): Name of the child logger. If None, caller's name is used.
            override (bool, optional): Override membership checks if supported by the logger.
            is_method (bool, optional): Flag indicating that this logger is tied to a method.

        Returns:
            Logger: A child logger instance.
        """
        if name is None:
            # If no name provided, try to get the caller's function name
            name = inspect.stack()[1].function

        kwargs['is_method'] = is_method

        base_logger = self.log_device or self.class_logger
        return base_logger.get_child(name, override=override, **kwargs)

    def create_logger(self, name=None, is_method=False, **kwargs):
        """
        Create a logger for a given name, defaults to the caller's function name if not provided.

        Parameters:
            name (str, optional): Logger name.
            is_method (bool, optional): Flag indicating that this logger is tied to a method.

        Returns:
            Logger: A new logger instance.
        """
        if name is None:
            name = inspect.stack()[1].function
        return self.create_child_logger(name=name, is_method=is_method, **kwargs)

    def __is_member__(self):
        """
        Checks whether the caller of this method is a member of the same class.
        If not, raises a PermissionError.

        This uses frame inspection to ensure that 'self' in the caller frame
        is an instance of the same class.
        """
        log_device = self.log_device.get_child("__is_member__")
        log = log_device

        current_frame = inspect.currentframe()
        caller_frame = current_frame.f_back
        caller_self = caller_frame.f_locals.get("self", None)

        log.internal("Checking if caller is a member of this class...")
        if not isinstance(caller_self, self.__class__):
            raise PermissionError(
                f"Access denied. Method can only be accessed by members of the same class. "
                f"{type(caller_self).__name__} is not a valid member."
            )

        log.internal(f"Access granted to {caller_self.__class__.__name__}")