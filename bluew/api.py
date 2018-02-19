"""
bluew.api
~~~~~~~~~

This module implement the Bluew API.

Basic usage:

    >>> import bluew
    >>> mac = 'xx:xx:xx:xx:xx'
    >>> attr = 'attrrr'
    >>> bluew.read_attribute(mac, attr)
    [b'0', b'0']


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from typing import List

from .connections import Connection
from .plugables import UsedEngine
from .device import Device
from .controller import Controller


def devices(*args, **kwargs) -> List[Device]:
    """Get list of devices around."""
    with UsedEngine(*args, **kwargs) as engine:
        return engine.devices


def controllers(*args, **kwargs) -> List[Controller]:
    """Get list of available controllers."""
    with UsedEngine(*args, **kwargs) as engine:
        return engine.controllers


def get_devices(*args, **kwargs) -> List[Device]:
    """Get list of devices around."""

    with UsedEngine(*args, **kwargs) as engine:
        return engine.get_devices()


def connect(mac: str, *args, **kwargs) -> None:
    """Connect to a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine(*args, **kwargs) as engine:
        return engine.connect(mac)


def disconnect(mac: str, *args, **kwargs) -> None:
    """Disconnect from a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine(*args, **kwargs) as engine:
        return engine.disconnect(mac)


def trust(mac: str, *args, **kwargs) -> None:
    """Trust a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine(*args, **kwargs) as engine:
        return engine.trust(mac)


def distrust(mac: str, *args, **kwargs) -> None:
    """Distrust a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine(*args, **kwargs) as engine:
        return engine.distrust(mac)


def pair(mac: str, *args, **kwargs) -> None:
    """Pair with a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine(*args, **kwargs) as engine:
        return engine.pair(mac)


def remove(mac: str, *args, **kwargs) -> None:
    """Remove a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine(*args, **kwargs) as engine:
        return engine.remove(mac)


def write_attribute(mac: str, attribute: str, data: List[int],
                    *args, **kwargs) -> None:
    """Write a bluetooth attribute on bluetooth device.
    :param mac: MAC address of bluetooth device.
    :param attribute: Bluetooth attribute to write to.
    :param data: Data to write to attribute.
    """

    with Connection(mac, *args, **kwargs) as connection:
        return connection.write_attribute(attribute, data)


def read_attribute(mac: str, attribute: str, *args, **kwargs) -> List[bytes]:
    """Read a bluetooth attribute on bluetooth device.
    :param mac: MAC address of bluetooth device.
    :param attribute: Bluetooth attribute to read.
    """

    with Connection(mac, *args, **kwargs) as connection:
        return connection.read_attribute(attribute)


def info(mac: str, *args, **kwargs) -> Device:
    """Get device info.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine(*args, **kwargs) as engine:
        return engine.info(mac)
