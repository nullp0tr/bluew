"""
bluew.devices
~~~~~~~~~~~~

This module provides a service object, that should be returned
by any EngineBluew when queried for device services.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from bluew.ppobj import PPObj


class BLEService(PPObj):
    """BLE service object."""

    def __init__(self, **kwargs):
        attrs = {'Primary', 'Device', 'UUID', 'Path', 'Includes'}
        super().__init__(attrs, **kwargs)
        self.primary = kwargs.get('Primary')
        self.device = kwargs.get('Device')
        self.UUID = kwargs.get('UUID')  # pylint: disable=invalid-name
        self.path = kwargs.get('Path')
        self.includes = kwargs.get('Includes')
