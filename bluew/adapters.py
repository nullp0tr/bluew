"""
bluew.devices
~~~~~~~~~~~~

This module provides a adapter object, that should be returned
by any EngineBluew when queried for available adapters.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class Adapter(object):
    """Bluetooth Adapter."""

    def __init__(self, **kwargs):
        attrs = {'Alias', 'Powered', 'UUIDs', 'Address',
                 'DiscoverableTimeout', 'Pairable', 'Discoverable',
                 'Class', 'Modalias', 'PairableTimeout', 'Discovering',
                 'Name', 'Path'}
        for key, value in kwargs.items():
            if key not in attrs:
                raise TypeError(
                    'BlAdapter should not have attribute ' + key)
            setattr(self, key, value)
        for attr in attrs:
            if attr not in self.__dict__:
                setattr(self, attr, None)

    def __str__(self):
        result = ''
        for key in self.__dict__:
            result += key + ': ' + str(getattr(self, key)) + '\n'
        return result[:-1]
