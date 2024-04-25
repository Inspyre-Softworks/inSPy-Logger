"""


Author: 
    Inspyre Softworks

Project:
    inSPy-Logger

File: 
    inspy_logger/common/meta/helpers/api/cache.py
 

Description:
    

"""
from cachetools import TTLCache
import json
from warnings import warn
from datetime import datetime


CACHE = TTLCache(maxsize=100, ttl=60*30)
"""The cache object."""


class CacheEntry:
    """
    A class to represent a cache entry.

    This class will represent a cache entry and provide methods to interact with the cache entry.

    Attributes:
        data:
            The data to cache.

        time_cached:
            The time the data was cached.

        age:
            The age of the cache entry.

    """

    def __init__(self, data, time_cached):
        """
        Initialize the cache entry.

        Parameters:
            data:
                The data to cache.

            time_cached:
                The time the data was cached.

        Attributes:
            data:
                The data to cache.

            time_cached:
                The time the data was cached.

            age:
                The age of the cache entry.

        """
        self.data = data
        self.time_cached = time_cached

    @property
    def age(self):
        """
        Get the age of the cache entry.

        Returns:
            The age of the cache entry.

        """
        return (datetime.now() - self.time_cached).total_seconds()

    def is_expired(self, ttl):
        """
        Check if the cache entry is expired.

        Parameters:
            ttl (int):
                The time to live for the cache entry.

        Returns:
            True if the cache entry is expired, False otherwise.

        """
        return (datetime.now() - self.time_cached).total_seconds() > ttl



# A decorator to cache the results of a function.
def cached_request(func):
    """
    Cache the return of a function.
    
    This decorator will cache the return of a function for a specified amount of time. This is useful for functions that
    make requests to APIs that have rate limits. The cache will prevent the function from being called until the cache
    TTL has expired.
    
    Parameters:
        func:
            The function to cache the return of.

    Returns:
        The cached results of the function.

    Example:
        >>> import requests
        >>> from inspy_logger.common.meta.helpers.api.cache import cached_request
        >>>
        >>> @cached_request
        ... def get_data():
        ...     return requests.get('https://api.example.com/data').json()

    """

    def wrapper(*args, force_refresh=False, **kwargs):
        """
        The wrapper function for the decorator.

        This function will cache the results of the decorated function and return the cached results if they exist.

        Parameters:
            *args:
                The arguments passed to the decorated function.

            force_refresh (bool):
                Whether to force a refresh of the cached data.

            **kwargs:
                The keyword arguments passed to the decorated function.

        Returns:
            If the data is cached, the cached data will be returned. Otherwise, the decorated function will be called

        """
        # Create a unique key for the query
        query_key = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)

        # Check if the data is cached
        cached_result = CACHE.get(query_key)
        if cached_result is not None and not force_refresh:
            return cached_result  # Return cached data
        elif force_refresh and cached_result:
            warn('Forcing refresh of cached data')

        result = func(*args, **kwargs)
        cache_entry = CacheEntry(result, datetime.now())
        CACHE[query_key] = cache_entry  # Cache the result

        return result

    return wrapper
