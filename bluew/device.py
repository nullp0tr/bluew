"""
bluew.devices
~~~~~~~~~~~~

This module provides a device object, that should be returned
by any EngineBluew when queried for devices.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from bluew.ppobj import PPObj


class Device(PPObj):  # pylint: disable=too-many-instance-attributes
    """Bluetooth device object."""

    def __init__(self, **kwargs):
        attrs = {'Adapter', 'Address', 'Alias', 'Appearance',
                 'Blocked', 'Connected', 'LegacyPairing',
                 'Name', 'Paired', 'ServicesResolved', 'Trusted',
                 'UUIDs', 'ManufacturerData', 'RSSI', 'Path',
                 'ServiceData', 'AddressType', 'Class', 'Icon',
                 'Modalias'}
        super().__init__(attrs, **kwargs)
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
