"""
bluew.dbusted.decorators
~~~~~~~~~~~~

This module contains some helper decorators for the dbusted engine.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from functools import wraps
from bluew.engine import EngineBluewError


def mac_to_dev(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        if '/dev_' not in dev:
            dev = '/dev_' + dev.replace(':', '_')
        return func(self, dev, *args, **kwargs)
    return wrapper


def check_availablity(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        available = self._get_device_or_timeout(dev)
        if not available:
            raise EngineBluewError(EngineBluewError.DEVICE_NOT_AVAILABLE)
        return func(self, dev, *args, **kwargs)
    return wrapper


def check_if_paired(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        paired = self.is_device_paired(dev, timeout=0)
        if paired:
            return True
        return func(self, dev, *args, **kwargs)
    return wrapper


def check_if_connected(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        connected = self.is_device_connected(dev)
        if not connected:
            return True
        return func(self, dev, *args, **kwargs)
    return wrapper
