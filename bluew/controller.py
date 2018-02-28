"""
bluew.devices
~~~~~~~~~~~~

This module provides a adapter object, that should be returned
by any EngineBluew when queried for available adapters.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from bluew.ppobj import PPObj


class Controller(PPObj):  # pylint: disable=too-many-instance-attributes
    """Bluetooth controller object."""

    def __init__(self, **kwargs):
        attrs = {'Alias', 'Powered', 'UUIDs', 'Address',
                 'DiscoverableTimeout', 'Pairable', 'Discoverable',
                 'Class', 'Modalias', 'PairableTimeout', 'Discovering',
                 'Name', 'Path', 'AddressType'}
        super().__init__(attrs, **kwargs)
        self.alias = kwargs.get('Alias')
        self.powered = kwargs.get('Powered')
        self.UUIDs = kwargs.get('UUIDs')  # pylint: disable=invalid-name
        self.address = kwargs.get('Address')
        self.discoverable_timeout = kwargs.get('DiscoverableTimeout')
        self.pairable = kwargs.get('Pairable')
        self.discoverable = kwargs.get('Discoverable')
        self.cls = kwargs.get('Class')
        self.modalias = kwargs.get('Modalias')
        self.pairable_timeout = kwargs.get('PairableTimeout')
        self.discovering = kwargs.get('Discovering')
        self.name = kwargs.get('Name')
        self.path = kwargs.get('Path')
        self.address_type = kwargs.get('AddressType')
