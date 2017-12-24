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
from .devices import Device


def get_devices() -> List[Device]:
    """Get list of devices around."""

    with UsedEngine() as engine:
        return engine.get_devices()


def connect(mac: str) -> None:
    """Connect to a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine() as engine:
        return engine.connect(mac)


def disconnect(mac: str) -> None:
    """Disconnect from a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine() as engine:
        return engine.disconnect(mac)


def trust(mac: str) -> None:
    """Trust a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine() as engine:
        return engine.trust(mac)


def distrust(mac: str) -> None:
    """Distrust a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine() as engine:
        return engine.distrust(mac)


def pair(mac: str) -> None:
    """Pair with a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine() as engine:
        return engine.pair(mac)


def remove(mac: str) -> None:
    """Remove a bluetooth device.
    :param mac: MAC address of bluetooth device.
    """

    with UsedEngine() as engine:
        return engine.remove(mac)


def write_attribute(mac: str, attribute: str, data: List[int]) -> None:
    """Write a bluetooth attribute on bluetooth device.
    :param mac: MAC address of bluetooth device.
    :param attribute: Bluetooth attribute to write to.
    :param data: Data to write to attribute.
    """

    with Connection(mac) as connection:
        return connection.write_attribute(attribute, data)


def read_attribute(mac: str, attribute: str) -> List[bytes]:
    """Read a bluetooth attribute on bluetooth device.
    :param mac: MAC address of bluetooth device.
    :param attribute: Bluetooth attribute to read.
    """

    with Connection(mac) as connection:
        return connection.read_attribute(attribute)


def info(mac: str) -> Device:
    """Get device info.
    :param mac: MAC address of bluetooth device.
    """

    with Connection(mac) as connection:
        return connection.info()
