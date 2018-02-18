"""
bluew.devices
~~~~~~~~~~~~

This module provides a device object, that should be returned
by any EngineBluew when queried for devices.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from bluew.ppobj import PPObj


class Device(PPObj):
    """Bluetooth device object."""

    def __init__(self, **kwargs):
        attrs = {'Adapter', 'Address', 'Alias', 'Appearance',
                 'Blocked', 'Connected', 'LegacyPairing',
                 'Name', 'Paired', 'ServicesResolved', 'Trusted',
                 'UUIDs', 'ManufacturerData', 'RSSI', 'Path',
                 'ServiceData', 'AddressType', 'Class', 'Icon',
                 'Modalias'}
        super().__init__(attrs, **kwargs)
