from os import makedirs
from pathlib import Path
from pickle import dump as pkl_dump
from pickle import load as pkl_load
from time import time

from appdirs import user_cache_dir
from domain_suffixes.suffixes import Suffixes
from humanize.time import precisedelta

PICKLE_FILEPATH = Path(
    user_cache_dir(
        appname='InspyLogger',
        appauthor='Inspyre-Softworks'
    )
).joinpath('tld.pkl')


class TLDCache(object):

    parent_dir = PICKLE_FILEPATH.parent

    def __init__(self):
        self.__created_ts = None
        self.__pickle_fp_exists = None
        self.__num_tlds = None
        self.__tlds = None
        self.__data = None
        self.__last_renewal_ts = None
        self.__renewal_hist = None

    def build(self):
        self.__data = {
                'created_ts': time(),
                'renewal_data': {
                        'last_ts': None,
                        'history': [],
                },
                'tlds': self.fetch_from_source()
        }

        return self.__data

    def load(self):
        """ Load the pickle file for the cache.

        Will attempt to load the pickle file into memory from the path indicated by :obj:`PICKLE_FILEPATH`

        Raises:
            :exception:`FileNotFoundError`: If the pickle file does not exist.

        """
        print('Loading pickle file')
        with open(PICKLE_FILEPATH, 'rb') as pfp:
            res = pkl_load(pfp)

        return res

    def write(self):
        """ Write the pickle file.

        Write the contents of the cache to the file-system path indicated by :obj:`PICKLE_FILEPATH`

        Raises:
            :exception:`PermissionError`: If the pickle file can't be written due to permissions writing the file to storage. 
        """

        if not self.parent_dir.exists():
            makedirs(self.parent_dir, exist_ok=True)

        with open(PICKLE_FILEPATH, 'wb') as pfp:
            pkl_dump(self.__data, pfp)

    def fetch_from_source(self):
        """ Fetch the top-level-domain list from the source

        Returns:
            :class:`list`: A list of all known top-level domain suffixes from the domain-suffixes package.
        """
        suffixes = Suffixes()
        return suffixes.get_all_tlds()

    @property
    def contents(self) -> dict:
        if self.__data is None:
            try:
                self.__data = self.load()
            except FileNotFoundError:
                self.__data = self.build()
                self.write()

        return self.__data

    @property
    def TLDs(self) -> list:
        """ Returns a list of TLDs (top-level domains) for validating against """
        return self.contents['tlds']

    @property
    def created_timestamp(self) -> float:
        """
        An alias for :attr:`created_ts`

        Returns:
            created_ts (float):
                The time (in seconds since Epoch) when the cache was created.

        """
        return self.created_ts

    @property
    def created_ts(self) -> float:
        """
        The time (in seconds since Epoch) when the cache was created
        """
        return self.contents['created_ts']

    @property
    def age_in_seconds(self) -> float:
        """
        The number of seconds that have elapsed since creation of the cache.
        """
        return time() - self.created_ts

    @property
    def age(self) -> str:
        return precisedelta(self.age_in_seconds)
