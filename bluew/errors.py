"""
bluew.errors
~~~~~~~~~~~~

This module contains the errors that should be raised by an engine.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class BluewError(Exception):
    """For those times when the Engine blows."""

    DEVICE_NOT_AVAILABLE = 'Bluew can not find bluetooth device'

    def __init__(self, reason, name='', version=''):
        super().__init__()
        self.engine_name = name
        self.version = version
        self.reason = reason

    def __str__(self):
        msg = self.reason + ' using: ' + self.engine_name
        msg += ' ver: ' + self.version
        return msg


class DeviceNotAvailable(BluewError):
    """
    This error should be raised by engines, when
    a device is not avialable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.DEVICE_NOT_AVAILABLE, *args, **kwargs)
