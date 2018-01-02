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
    CONTROLLER_NOT_READY = 'The controller might be blocked/disabled.'
    COULD_NOT_PAIR = 'Bluew could not pair with device.'
    READ_WRITE_FAILED = 'Bluew could not read/write this attribute.'
    INVALID_ARGS = 'Invalid args.'
    UNEXPECTED_ERROR = 'An unexpected error happened.'

    def __init__(self, reason, long_reason='', name='', version=''):
        super().__init__()
        self.engine_name = name
        self.version = version
        self.reason = reason
        self.long_reason = long_reason

    def __str__(self):
        msg_tail = ' using: ' + self.engine_name + ' ver: ' + self.version
        if self.long_reason:
            msg = self.long_reason + msg_tail
            return msg
        msg = self.reason + msg_tail
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
    This error is raised when a pairing error that can't be handled is raised.
    """

    AUTHENTICATION_ERROR = 'Failed to authenticate'

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.COULD_NOT_PAIR, *args, **kwargs)


class ReadWriteNotifyError(BluewError):
    """
    This error is raised when a read/write fail that can't be handled happens.
    """

    NOT_PERMITTED = '''Action not allowed on this attribute.'''
    NOT_SUPPORTED = '''This attribute doesn't support this action'''
    NOT_AUTHORIZED = '''Client not trusted by device.'''
    IN_PROGRESS = '''There's already a read/write op on this attribute.'''

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.READ_WRITE_FAILED, *args, **kwargs)


class InvalidArgumentsError(BluewError):
    """
    This error is rasied when arguemnts passed are.. well.. invalid.
    """

    INVALID_LEN = '''Length of passed argument isn't valid.'''
    INVALID_ARGS = '''The arguments passed are incorrect.'''

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.INVALID_ARGS, *args, **kwargs)


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


class ControllerNotReady(BluewError):
    """
    This error is raised when the controller specified or picked by default
    is not ready.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(BluewError.CONTROLLER_NOT_READY, *args, **kwargs)
