"""
bluew.devices
~~~~~~~~~~~~

This module provides a device object, that should be returned
by any EngineBluew when queried for devices.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class Device(object):
    """Bluetooth device object."""

    def __init__(self, **kwargs):
        attrs = {'Adapter', 'Address', 'Alias', 'Appearance',
                 'Blocked', 'Connected', 'LegacyPairing',
                 'Name', 'Paired', 'ServicesResolved', 'Trusted',
                 'UUIDs', 'ManufacturerData', 'RSSI', 'Path',
                 'ServiceData'}
        for key, value in kwargs.items():
            if key not in attrs:
                raise TypeError(
                    'Device should not have attribute ' + key)
            setattr(self, key, value)

    def __str__(self):
        result = ''
        for key in self.__dict__:
            result += key + ': ' + str(getattr(self, key)) + '\n'
        return result
