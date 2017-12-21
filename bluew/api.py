"""
bluew.api
~~~~~~~~~

This module implement the Bluew API.

Basic usage:

    >>> import bluew
    >>> mac = 'xx:xx:xx:xx:xx'
    >>> attr = 'attrrr'
    >>> bluew.read_attribute(mac, attr)


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from .connections import Connection
from .plugables import UsedEngine


def get_devices():
    """Get list of devices around."""

    # engine = UsedEngine()
    # engine.start_engine()
    # devices = engine.get_devices()
    # engine.stop_engine()
    with UsedEngine() as engine:
        return engine.get_devices()


def pair(mac):
    """Pair with a bluetooth device.

    :param mac: MAC address of bluetooth device.
    :return: bluew.Response.
    """

    with Connection(mac) as connection:
        return connection.pair()


def trust(mac):
    """Trust a bluetooth device.

    :param mac: MAC address of bluetooth device.
    :return: bluew.Response.
    """

    with Connection(mac) as connection:
        return connection.trust()


def write_attribute(mac, attribute, data):
    """Write a bluetooth attribute on bluetooth device

    :param mac: MAC address of bluetooth device.
    :param attribute: Bluetooth attribute to write to.
    :param data: Data to write to attribute.
    :return: bluew.Response.
    """

    with Connection(mac) as connection:
        return connection.write_attribute(attribute, data)


def read_attribute(mac, attribute):
    """Read a bluetooth attribute on bluetooth device

    :param mac: MAC address of bluetooth device.
    :param attribute: Bluetooth attribute to read.
    :return: bluew.Response.
    """

    with Connection(mac) as connection:
        return connection.read_attribute(attribute)


def info(mac):
    """Get device info.

    :param mac: MAC address of bluetooth device.
    :return: bluew.DataResponse.
    """

    with Connection(mac) as connection:
        return connection.info()
