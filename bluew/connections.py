"""
bluew.connections
~~~~~~~~~~~~~~~~~

This module provides a Connection object to manage connections
with one device.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from functools import wraps
import bluew.plugables
from bluew.daemon import Daemon, daemonize


UsedEngine = bluew.plugables.UsedEngine


def close_on_error(func):
    """
    This decorator makes sure that an object's close() method
    is called when an error occurs.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        """This function wraps the function passed to close_on_error()"""
        try:
            return func(self, *args, **kwargs)
        except Exception as exp:
            self.close()
            raise exp
    return wrapper


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
        self.keep_alive = kwargs.get('keep_alive', True)
        self.engine = UsedEngine(*args, **kwargs)
        self.mac = mac
        self._connect()
        self.daemon = Daemon()

    def __enter__(self):
        return self

    @close_on_error
    def _connect(self):
        self.engine.start_engine()
        self.engine.connect(self.mac)

    @close_on_error
    def _disconnect(self):
        self.engine.disconnect(self.mac)

    @close_on_error
    @daemonize
    def pair(self):
        """Pair with bluetooth device."""
        return self.engine.pair(self.mac)

    @close_on_error
    def trust(self):
        """Trust a bluetooth device."""
        return self.engine.trust(self.mac)

    @close_on_error
    def write_attribute(self, attribute, data):
        """Write to a bluetooth attribute."""
        return self.engine.write_attribute(self.mac, attribute, data)

    @close_on_error
    def read_attribute(self, attribute):
        """Read a bluetooth attribute."""
        return self.engine.read_attribute(self.mac, attribute)

    @close_on_error
    def info(self):
        """Get device info."""
        return self.engine.info(self.mac)

    @property  # type: ignore
    @close_on_error
    def services(self):
        """Get available BLE services of a device."""
        return self.engine.get_services(self.mac)

    @property  # type: ignore
    @close_on_error
    def chrcs(self):
        """Get available BLE characteristics of a device."""
        return self.engine.get_chrcs(self.mac)

    @close_on_error
    def notify(self, attribute, handler):
        """Turn on notifications on attribute, and call handler with data."""
        return self.engine.notify(self.mac, attribute, handler)

    @close_on_error
    def stop_notify(self, attribute):
        """Turn off notifications on attribute."""
        return self.engine.stop_notify(self.mac, attribute)

    @close_on_error
    def remove(self):
        """Disconnect and unpair device."""
        return self.engine.remove(self.mac)

    def close(self):
        """Close the conncection."""
        if not self.keep_alive:
            self.remove()
        self.engine.stop_engine()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
