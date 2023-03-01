import logging


class SuppressFileFilter(logging.Filter):
    def __init__(self, file_name):
        super(SuppressFileFilter, self).__init__()
        self.file_name = file_name

    def filter(self, record):
        return not record.filename.endswith(self.file_name)

