"""
network.py

Description:
    Contains helper code pertaining to networks.

File:
    PROJECT_ROOT/inspy_logger/helpers/network.py

Project:
    Inspy-Logger

Author:
    Inspyre Softworks
        - Taylor-Jayde Blackstone <t.blackstone@inspyre.tech>

Since Version:
    2.1

Date:
    10/25/2022 - 03:28hrs

"""

# Do our import
from urllib.parse import quote as url_safe

import requests

from inspy_logger.helpers.cache import TLDCache

DEFAULT_TEST_HOSTS = [
        ['https', 'inspyre', 'tech'],
        ['https', 'google', 'com']
]
"""
:obj:`list`[:obj:`list`[:obj:`str`]]:
        The hosts provided by default to test connectivity against.
"""

hosts = []
"""
:obj:`list`[:obj:`Host`]: 
    A list of host objects that will be used to connect to. 
"""

TLD_CACHE = TLDCache()

VALID_TLDS = TLD_CACHE.TLDs


class Host():
    def __init__(self, host: list):

        # Populate the .__incoming variable with the URL parts
        # provided by the 'host' parameter
        self.__incoming = host

        # Set placeholders for all other host properties.
        self.__host_name = None
        self.__status = None
        self.__URL = None

    class URLObj():
        """
        A class to contain important URL properties.
        """

        def __init__(self, url_parts: list[str]):
            """
            Instantiate a new URLObj instance.



            Args:
                url_parts (:class:`list[:obj:``str``]`):
                    Pass in a list of url parts that will be unpacked into the class properties

            Returns:
                :class:`URLObj`

            """
            # Unpack our incoming URL parts into protected variables that
            # will be accessible via class properties.
            self.__protocol, self.__host_name, self.__tld = url_parts
            self.__valid_protocols = [
                    'http',
                    'https',
            ]

        @property
        def host_name(self) -> str:
            """ Return the host name associated with this instance.

            The value of this property is filled by the the contents of the 'url_parts'
            parameter (provided on instantiation) or via this property's setter.

            Returns:
                str:
                    The host_name associated with this instance.

            Raises:
                :exception:`TypeError` if the value of this property is not set to a string.

            """
            return self.__host_name

        @host_name.setter
        def host_name(self, new):
            if not isinstance(new, str):
                raise TypeError('The new value must be a string!')

            new = url_safe(new)

            self.__host_name = new

        @property
        def protocol(self) -> str:
            """
            str: The URLs protocol string.

            Note:
                This property must be set to a string value that is one of the following;

                    * 'http'
                    * 'https'

            Raises:
                :exception:`ValueError` if the value is not set to a valid protocol string.

            """
            return self.__protocol

        @protocol.setter
        def protocol(self, new: str):
            if new.lower() not in self.valid_protocols:
                raise ValueError(
                    f'The protocol must be one of {",".join(self.__valid_protocols)}.')

            self.__protocol = new

        @property
        def valid_protocols(self):
            """
            list: A list of valid protocol strings.
            """
            return self.__valid_protocols

        @property
        def valid_top_level_domains(self):
            """
            :obj:`list` of :obj:`str`:  A list of valid top-level domain strings.
            """
            return VALID_TLDS

        @property
        def tld(self) -> str:
            """
            The tld function returns the top-level domain of a given URL.

            Returns:
                str: The top level domain of the url

            """
            return self.__tld

        @tld.setter
        def tld(self, new):
            if not isinstance(new, str):
                raise TypeError(f"New value must be a string not {type(new)}")
            if new not in TLD_CACHE.TLDs:
                raise ValueError("TLD must be valid!")

            self.__tld = new

        @property
        def formatted(self):
            """
            The formatted function returns a string of the URL in the format:
            protocol://host_name.tld

            Example:
                Use this when you wanna get the URL in string format::
                    >>> from inspy_logger.helpers.network import Host
                    >>> host = Host(['https', 'inspyre', 'tech'])
                    >>> print(host.URL.formatted)

                    'https://inspyre.tech'

            Returns:
                A string that is the concatenation of all 3 URL parts;

                - Protocol
                - Host Name,
                - Top level domain (TLD)


            """
            return f"{self.protocol}://{self.host_name}.{self.tld}"

        @property
        def as_dict(self):
            """
            The as_dict function returns a dictionary containing the following:
                - formatted:
                    The URL as a string, e.g. 'http://google.com'
                - parts:
                    A dictionary containing the protocol, host_name and TLD of the URL
                        - protocol:
                            The protocol used to access this host (e.g., http)
                        - host_name:
                            The name of the server that hosts this host (e.g., google)
                        - TLD:
                            The top-level domain for this host (e.g., com)

            Args:
                self: Refer to the object itself

            Returns:
                A dictionary with the following keys:

                * formatted
                * parts
                    - protocol
                    - host_name
                    - TLD
                * reachable
            """
            return dict(
                {
                        'formatted': self.formatted,
                        'parts':     {
                                'protocol':  self.protocol,
                                'host_name': self.host_name,
                                'TLD':       self.tld
                        },
                        'reachable': None
                }
            )

    @property
    def host_name(self) -> (str | None):
        """ Return the name of the host. """

        if self.__host_name is None:
            self.__host_name = self.__incoming[1].lower()

        return self.__host_name

    @property
    def valid_status_codes(self) -> list:
        """ Returns the valid status codes for the host. """
        return ['UP', 'DOWN']

    @property
    def status(self) -> str:
        """
        The online status of the host.

        Can be one of:
            * UP:
                This would indicate that we've tested connectivity to this host and were able to establish a connection.

            * DOWN:
                This would indicate that we've tested the connectivity to this host and were unable to establish a connection.

        """
        return self.__status

    @status.setter
    def status(self, new):
        if new.upper() not in self.valid_status_codes:
            raise ValueError('Invalid status code')

        self.__status = new.upper()

    @property
    def can_connect(self) -> (bool | None):
        """
        The can_connect function is a helper function that checks if the server is up and running.
        It returns True if it can connect to the host, False otherwise.


        Returns:
            A boolean value

        """
        if self.status is not None:
            return self.status != 'DOWN'

    @property
    def URL(self):
        """
        The URL property returns the URL property.

        Returns:
            :class:`inspy_logger.helpers.networks.Host.URLObj`

        """
        if self.__URL is None:
            self.__URL = self.URLObj(self.__incoming)

        return self.__URL

    def check_connectivity(self, timeout):
        """
        The check_connectivity function checks the connectivity of a given URL.
        It returns 'UP' if the connection is successful, and 'DOWN' otherwise.

        Parameters:
            timeout (int):
                The number of seconds to wait for the connection to be established. (Required)

        Returns:
            The status of the host:

                - "UP":
                    The host is reachable.

                - "DOWN":
                    The host is unreachable.
        """
        try:
            requests.head(
                self.URL.formatted,
                timeout = timeout
            )
            self.status = 'UP'

        except requests.ConnectionError:
            self.status = 'DOWN'

        return self.status


def check_connectivity(
        test_hosts=None,
        timeout=3,
        online_if_any=True,
        online_if_all=False
):
    """
    The check_connectivity function checks the connectivity of a list of hosts.

    Parameters:
        test_hosts (list):
            A list of hosts to test connectivity to.

        timeout (int):
            The number of seconds to wait for a connection to be established. (Defaults to 3)

        online_if_any (bool):
            Whether the function should consider us online if any of the hosts are connectable.
            (Defaults to True)

        online_if_all (bool):
            Whether the function should only consider us online if all of the hosts are connectable.
            (Defaults to False)

    Returns:
        bool:
            True: Connectivity check passed successfully.
            False: Connectivity check failed.
    """
    if test_hosts is None:
        test_hosts = DEFAULT_TEST_HOSTS

    for host in test_hosts:
        hosts.append(Host(host))

    if online_if_any and online_if_all:
        raise ValueError('Both online_if_any and online_if_all cannot be True')

    statuses = [host.check_connectivity(timeout = timeout) for host in hosts]

    if online_if_any:
        return 'UP' in statuses

    if online_if_all:
        return 'DOWN' in statuses
