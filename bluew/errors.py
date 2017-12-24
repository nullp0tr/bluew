"""
bluew.errors
~~~~~~~~~~~~

This module contains the errors that should be raised by an engine.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class BluewError(Exception):
    """For those times when the Engine blows."""

    DEVICE_NOT_AVAILABLE = 'Bluew can not find bluetooth device.'
    NO_CONTROLLERS = 'Bluew could not find any bluetooth controllers.'
    CONTROLLER_NOT_AVAILABLE = 'Bluew could not find the controller specified.'
    COULD_NOT_PAIR = 'Bluew could not pair with device.'

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
    This error is raised by when the bluetooth devices specified
    is not found.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.DEVICE_NOT_AVAILABLE, *args, **kwargs)


class PairError(BluewError):
    """
    This error is raised by when the bluetooth devices specified
    is not found.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.COULD_NOT_PAIR, *args, **kwargs)


class NoControllerAvailable(BluewError):
    """
    This error is raised when no bluetooth controllers
    are found.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.NO_CONTROLLERS, *args, **kwargs)


class ControllerSpecifiedNotFound(BluewError):
    """
    This error is raised when the controller specified
    is not found by bluew.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.CONTROLLER_NOT_AVAILABLE, *args, **kwargs)
