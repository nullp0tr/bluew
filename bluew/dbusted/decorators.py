"""
bluew.dbusted.decorators
~~~~~~~~~~~~

This module contains some helper decorators for the dbusted engine.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from functools import wraps
from bluew.errors import DeviceNotAvailable
from bluew.dbusted.interfaces import BluezInterfaceError as IfaceError


def mac_to_dev(func):
    """Convert a mac address to a device path."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        if '/dev_' not in dev:
            dev = '/dev_' + dev.replace(':', '_')
        return func(self, dev, *args, **kwargs)
    return _wrapper


def check_if_available(func):
    """Check if bluetooth device is available before performing action."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        # pylint: disable=W0212
        available = self._is_device_available(dev)
        if available:
            return func(self, dev, *args, **kwargs)
        raise DeviceNotAvailable(name=self.name, version=self.version)
    return _wrapper


def check_if_not_paired(func):
    """Check if device is paired."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        # pylint: disable=W0212
        paired = self._is_device_paired_timeout(dev)
        if not paired:
            return func(self, dev, *args, **kwargs)
        return
    return _wrapper


def check_if_connected(func):
    """Check if device is connected."""
    @wraps(func)
    def _wrapper(self, dev, *args, **kwargs):
        # pylint: disable=W0212
        connected = self._is_device_connected(dev)
        if connected:
            return func(self, dev, *args, **kwargs)
        return
    return _wrapper


def handle_errors(func):
    """Handle errors of interface calls."""
    @wraps(func)
    def _wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except IfaceError as exp:
            # pylint: disable=W0212
            self._handle_errors(exp, *args, **kwargs)
    return _wrapper
