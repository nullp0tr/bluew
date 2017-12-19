"""
bluew.devices
~~~~~~~~~~~~

This module provides a ble characteristic object, that should be returned
by any EngineBluew when queried for available characteristics of a device.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class BLECharacteristic(object):
    """BLE Characteristic."""

    def __init__(self, **kwargs):
        attrs = {'Value', 'Flags', 'Notifying', 'Service', 'UUID', 'Path'}
        for key, value in kwargs.items():
            if key not in attrs:
                raise TypeError(
                    'BleCharacteristic should not have attribute ' + key)
            setattr(self, key, value)

    def __str__(self):
        result = ''
        for key in self.__dict__:
            result += key + ': ' + str(getattr(self, key)) + '\n'
        return result
