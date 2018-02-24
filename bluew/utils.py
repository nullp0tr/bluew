"""
bluew.utils
~~~~~~~~~~~

This module provides a couple of helper/utility functions that can be useful
for certain situations.
"""


import typing as typ
import bluew
from .device import Device


def devs_with_uuid(uuid: str) -> typ.List[Device]:
    """
    Get a list of devices with a specific UUID.
    This function can be useful when you wanna connect to any device with a
    certain model, but don't care which one it is.
    """

    devices = bluew.devices()
    devices_ = []
    for dev in devices:
        for uuid_ in getattr(dev, 'UUIDs'):
            if uuid_ == uuid:
                devices_.append(dev)
    return devices_
