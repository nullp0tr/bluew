"""
bluew.devices
~~~~~~~~~~~~

This module provides a device object, that should be returned
by any EngineBluew when queried for devices.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


import bluew
from bluew.ppobj import PPObj


class Device(PPObj):  # pylint: disable=too-many-instance-attributes
    """Bluetooth device object."""
    attrs = {'Adapter', 'Address', 'Alias', 'Appearance',
             'Blocked', 'Connected', 'LegacyPairing',
             'Name', 'Paired', 'ServicesResolved', 'Trusted',
             'UUIDs', 'ManufacturerData', 'RSSI', 'Path',
             'ServiceData', 'AddressType', 'Class', 'Icon',
             'Modalias'}

    def __init__(self, **kwargs):
        super().__init__(Device.attrs, **kwargs)
        self.adapter = kwargs.get('Adapter')
        self.address = kwargs.get('Address')
        self.alias = kwargs.get('Alias')
        self.appearance = kwargs.get('Appearance')
        self.blocked = kwargs.get('Blocked')
        self.connected = kwargs.get('Connected')
        self.legacy_pairing = kwargs.get('LegacyPairing')
        self.name = kwargs.get('Name')
        self.paired = kwargs.get('Paired')
        self.services_resolved = kwargs.get('ServicesResolved')
        self.trusted = kwargs.get('Trusted')
        self.UUIDs = kwargs.get('UUIDs')  # pylint: disable=invalid-name
        self.manufacturer_data = kwargs.get('ManufacturerData')
        self.RSSI = kwargs.get('RSSI')  # pylint: disable=invalid-name
        self.path = kwargs.get('Path')
        self.service_data = kwargs.get('ServiceData')
        self.address_type = kwargs.get('AddressType')
        self.cls = kwargs.get('Class')
        self.icon = kwargs.get('Icon')
        self.modalias = kwargs.get('Modalias')

    def __getattribute__(self, item):
        # This hack queries the state of the device on attribute access, and
        # guarantees that all values returned are in fact up to date.
        # IMPORTANT NOTE: Thou shall not use `self.attr` access in this method,
        # or thou shall dive in an infinite recursion as deep as thy stack.
        # SERIOUSLY: `self.attr` is just gonna call this method again.
        if item not in Device.attrs:
            mac = super().__getattribute__('address')
            self = bluew.info(mac)  # noqa: F841
        return super().__getattribute__(item)
