import inspect
from inspy_logger import LOG_DEVICE, Logger



class LoggableDescriptor:
    """
    Descriptor for accessing a logger specific to a class method.
    """

    def __get__(self, instance, owner):
        if instance is None:
            # Accessing through the class, not an instance
            return owner.class_logger

        # Determine the calling method's name
        stack = inspect.stack()
        # Start from 1 to skip the current __get__ frame
        for frame_record in stack[1:]:
            if 'self' in frame_record.frame.f_locals and frame_record.frame.f_locals['self'] is instance:
                method_name = frame_record.function
                print(method_name)
                break
        else:
            raise Exception("Could not determine the calling method's name.")

        # Get a child logger named after the class and method
        return instance.log_device.get_child(method_name)


def _get_parent_logging_device():
    """
    Determines the parent logging device by inspecting the caller's log_device or parent_log_device attribute.

    Returns:
        Logger: The parent logging device.
    """
    LOG_DEVICE.debug("Determining parent logging device")
    caller_frame = inspect.currentframe().f_back
    caller_locals = caller_frame.f_locals

    if "logger" in caller_locals:
        return caller_locals["logger"]
    elif "parent_log_device" in caller_locals:
        return caller_locals["parent_log_device"]
    else:
        raise ValueError("Unable to determine the parent logging device.")


class Loggable:
    """
    A metaclass to enhance classes with logging capabilities. Classes that inherit from
    'Loggable' can instantly access a logger without manually setting it up. This logger
    is derived from a parent logger, ensuring consistent logging behavior and hierarchy.

    Attributes:
        - log_device: The logger device associated with the instance of the class.
    """
    method_logger = LoggableDescriptor()
    class_logger = None

    def __init__(self, parent_log_device=None, **kwargs):
        """
        Initializes an instance of the class.

        Args:
            parent_log_device (optional): The parent log device. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            None
        """
        self.parent_log_device = parent_log_device
        self.__log_name = self.__class__.__name__
        if self.parent_log_device is not None:
            self.__log_device = self.parent_log_device.get_child(self.__log_name)
        else:
            self.__log_device = _get_parent_logging_device().get_child()

        # Set up class-level logger if it's not already set
        if self.__class__.class_logger is None:
            self.__class__.class_logger = self.__log_device

        self.method_logger = self.__class__.method_logger.logger

    @property
    def log_device(self):
        return self.__log_device

    @log_device.setter
    def log_device(self, new):
        if not isinstance(new, Logger):
            raise TypeError('log_device must be of type "Logger"')

        self.__log_device = new

    def create_child_logger(self, name=None, override=False):
        """
        Creates and returns a child logger of this object's logger.

        Parameters:
            name (str, optional): The name of the child logger.
                If not provided, the name of the calling function is used.
            override (bool, optional): A flag to override the membership check. Defaults to False.

        Returns:
            Logger: An instance of the Logger class that represents the child logger.
        """
        if not override:
            self.__is_member__()

        if name is None:
            name = inspect.stack()[1][
                3
            ]  # Get the name of the calling function if no name is provided
        #print(inspect.stack()[1])
        return self.log_device.get_child(name)

    def __is_member__(self):
        """
        Checks whether the caller of this method is a member of the same class.

        Raises:
            PermissionError: If the caller of this method is not a member of the same class.
        """
        log_device = self.log_device.get_child("__is_member__")
        log = log_device.logger

        current_frame = inspect.currentframe()
        log.debug(f"Current frame: {current_frame}")

        caller_frame = current_frame.f_back
        log.debug(f"Caller frame: {caller_frame}")

        caller_self = caller_frame.f_locals.get("self", None)
        log.debug(f"Caller self: {caller_self}")

        log.debug("Checking if caller is a member of this class...")
        if not isinstance(caller_self, self.__class__):
            raise PermissionError(
                "Access denied.\n"
                f"Method can only be accessed by members of the same class. {caller_self.__class__.__name__} is not such a member"
            )

        log.debug(f"Access granted to {caller_self.__class__.__name__}")
