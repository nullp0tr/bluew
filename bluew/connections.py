"""
bluew.connections
~~~~~~~~~~~~~~~~~

This module provides a Connection object to manage connections
with one device.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from .plugables import UsedEngine
from .responses import ConnectFailedResponse


class Connection:
    """A Bluew Connection

    Provides a persistent connection with one device.

    Basic Usage:

        >>> import bluew
        >>> mac = 'xx:xx:xx:xx:xx'
        >>> device = bluew.Connection(mac)
        >>> device.info()

    """

    def __init__(self, mac, *args, **kwargs):
        self.engine = UsedEngine(*args, **kwargs)
        self.mac = mac
        self._connect()

    def __enter__(self):
        return self

    def _connect(self):
        response = self.engine.connect(self.mac)
        if response == ConnectFailedResponse():
            raise BluewConnectionError()

    def _disconnect(self):
        self.engine.disconnect(self.mac)

    def pair(self):
        """Pair with bluetooth device."""
        return self.engine.pair(self.mac)

    def trust(self):
        """Trust a bluetooth device."""
        return self.engine.trust(self.mac)

    def write_attribute(self, attribute, data):
        """Write to a bluetooth attribute."""
        return self.engine.write_attribute(self.mac, attribute, data)

    def read_attribute(self, attribute):
        """Read a bluetooth attribute"""
        return self.engine.read_attribute(self.mac, attribute)

    def info(self):
        """Get device info"""
        return self.engine.info(self.mac)

    def close(self):
        """Close the conncection."""

        self._disconnect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class BluewConnectionError(Exception):
    """ConnectionError is raised when not able to connect"""

    def __str__(self):
        return "Bluew was not able to connect to device."
