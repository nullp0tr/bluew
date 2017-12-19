"""
bluew.connections
~~~~~~~~~~~~~~~~~

This module provides a Connection object to manage connections
with one device.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


import bluew.plugables


UsedEngine = bluew.plugables.UsedEngine


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
        self.keep_alive = kwargs.get('keep_alive', False)
        self.engine = UsedEngine(*args, **kwargs)
        self.mac = mac
        self._connect()

    def __enter__(self):
        return self

    def _connect(self):
        self.engine._register_agent()
        self.engine.remove(self.mac)
        self.engine.connect(self.mac)


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
        """Read a bluetooth attribute."""
        return self.engine.read_attribute(self.mac, attribute)

    def info(self):
        """Get device info."""
        return self.engine.info(self.mac)

    def get_controllers(self):
        """Get available bluetooth controllers."""
        return self.engine.get_controllers()

    def get_devices(self):
        """Get available bluetooth devices."""
        return self.engine.get_devices()

    def notify(self, attribute, handler):
        """Turn on notifications on attribute, and call handler with data."""
        return self.engine.notify(self.mac, attribute, handler)

    def stop_notify(self, attribute):
        """Turn off notifications on attribute."""
        return self.engine.stop_notify(self.mac, attribute)

    def close(self):
        """Close the conncection."""
        self.engine.remove(self.mac)
        self._disconnect()
        self.engine._unregister_agent()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.keep_alive:
            self.close()


class BluewError(Exception):
    """ConnectionError is raised when not able to connect"""

    def __str__(self):
        return "Bluew was not able to connect to device."
