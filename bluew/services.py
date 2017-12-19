"""
bluew.devices
~~~~~~~~~~~~

This module provides a service object, that should be returned
by any EngineBluew when queried for device services.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class BLEService(object):
    """BLE service object."""

    def __init__(self, **kwargs):
        attrs = {'Primary', 'Device', 'UUID', 'Path'}
        for key, value in kwargs.items():
            if key not in attrs:
                raise TypeError(
                    'BleService should not have attribute ' + key)
            setattr(self, key, value)

    def __str__(self):
        result = ''
        for key in self.__dict__:
            result += key + ': ' + str(getattr(self, key)) + '\n'
        return result
