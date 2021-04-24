"""

Contains exceptions for InspyLogger

"""
import inspect


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
