"""
bluew.dbusted.decorators
~~~~~~~~~~~~

This module contains some helper decorators for the dbusted engine.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from functools import wraps
from bluew.errors import DeviceNotAvailable


def mac_to_dev(func):
    """Convert a mac address to a device path."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        if '/dev_' not in dev:
            dev = '/dev_' + dev.replace(':', '_')
        return func(self, dev, *args, **kwargs)
    return _wrapper


def check_availablity(func):
    """Check if bluetooth device is available before performing action."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        # pylint: disable=W0212
        available = self._is_device_available(dev)
        if not available:
            raise DeviceNotAvailable(name=self.name, version=self.version)
        return func(self, dev, *args, **kwargs)
    return _wrapper


def check_if_paired(func):
    """Check if device is paired."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        # pylint: disable=W0212
        paired = self._is_device_paired_timeout(dev, timeout=1)
        if paired:
            return True
        return func(self, dev, *args, **kwargs)
    return _wrapper


def check_if_connected(func):
    """Check if device is connected."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        # pylint: disable=W0212
        connected = self._is_device_connected(dev)
        if not connected:
            return True
        return func(self, dev, *args, **kwargs)
    return _wrapper
