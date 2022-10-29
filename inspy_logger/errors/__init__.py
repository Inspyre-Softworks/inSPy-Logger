"""

Contains exceptions for InspyLogger

"""
import inspect


class InSPyLoggerError(Exception):
    frame = inspect.stack()[1]
    caller_name = frame[3]

    # Let's set a general error message for the parent exception
    # letting the end-user know that the child exception is
    # of this type;
    p_message = f"InSPyLogger has encountered an error! [Caller: {caller_name}]\n"

    def __init__(self, message=None, skip_print=False):
        # If the child exception provides a message we can introduce this with
        # the following phrase;
        msg_prefix = f'\nSome further context...\n'

        # If we're provided a message on instantiation we'll prepend our prefix
        # to it while assigning it to the :var:`message` variable. If no message
        # was provided :var:`message' will evaluate to str('')
        message = f'{msg_prefix} - {message}' if message is not None else ''

        # Assign our prefix string to a class attribute for easy debugging later.
        self.msg_prefix = msg_prefix

        # finally; concatenate the entirety of the error message delivered on raise.
        self.message = f"{self.p_message}{self.msg_prefix}- {self.message}"

        if not skip_print:
            print(self.message)


class DeviceNotStartedError(InSPyLoggerError):
    # Let's set a more specific message for the child exception.
    message = "[Device Not Started]\n" \
              "The root logging device has not yet been started! Try `isl.device.start()`\n    "
    prefix = "Some further information from the caller:\n"

    __child_frame = inspect.stack()[1]
    __child_frame_name = __child_frame[3]

    def __init__(self, message=None, skip_print=False):

        # Prettify our base message string.
        self.message = f"[{self.__class__.__name__}] [{self.__child_frame_name}] - {self.message}"

        message = f"{self.prefix} - {message}" if message is not None else ''

        self.message += message

        super(DeviceNotStartedError, self).__init__(message = self.message, skip_print = skip_print)


class DeviceAlreadyStartedError(InSPyLoggerError):
    # Let's set a more specific message for the child exception.
    message = "[Device Already Started] The device is already started.\n" \
              "The logging device is already instantiated and started."
    prefix = "Some futher information from the caller:\n"

    def __init__(self, message=None, skip_print=False):
        self.__child_caller_frame = inspect.stack()[1]
        self.__child_caller_name = self.__child_caller_frame[3]

        # Prettify our base message string.
        self.message = f"[{self.__class__.__name__}] - {self.message}"

        message = f"{self.prefix} - {message}" if message is not None else ''

        self.message += message

        super(DeviceAlreadyStartedError, self).__init__(message = self.message, skip_print = skip_print)



class ManifestEntryExistsError(Exception):
    def __init__(self, msg=None, caller_name=None):
        """
        
        Raise an exception advising an attempted log creation caller that there's already an entry for this logger on the manifest.

        """

        if msg is None:
            msg = "You've attempted to add a a previously existing logger to the log manifest"

        if caller_name is None:
            frame = inspect.stack()[1]
            caller_name = frame[3]

        self.message = str(f"{msg} | Caller: {caller_name}")
