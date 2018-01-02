"""
bluew.devices
~~~~~~~~~~~~

This module provides a adapter object, that should be returned
by any EngineBluew when queried for available adapters.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from bluew.ppobj import PPObj


class Controller(PPObj):
    """Bluetooth controller object."""

    def __init__(self, **kwargs):
        attrs = {'Alias', 'Powered', 'UUIDs', 'Address',
                 'DiscoverableTimeout', 'Pairable', 'Discoverable',
                 'Class', 'Modalias', 'PairableTimeout', 'Discovering',
                 'Name', 'Path', 'AddressType'}
        super().__init__(attrs, **kwargs)
