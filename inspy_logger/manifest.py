from time import time
from logging import getLogger
from box import Box


class Manifest(object):
    def __init__(self, root_name, root_device, calling_file, line_num):
        self.name = root_name

        self.contents = None
        self.add(root_name, root_device, calling_file, line_num)

    def check(self, name):

        return self.contents[name]['device'] if name in self.contents.keys() else None


    def add(self, name, logger_device, calling_file, line_num):
        """

        Add the provided logger to the manifest.

        Parameters:
          name (str): The logger name.
          logger_device ()

        """

        entry = {
                name: {
                        'created-ts':  time(),
                        'device':      logger_device,
                        'caller_file': calling_file,
                }
        }

        if self.contents is None:
            self.contents = Box(entry)
        else:
            self.contents.update(entry)
