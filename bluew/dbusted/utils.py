"""
bluew.dbusted.utils
~~~~~~~~~~~~~~~~~

This module provides helper functions for working with dbus.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

import dbus


def dbus_object_parser(dbus_object):
    """
    Convert dbus objects into native python objects.
    :param dbus_object: object to convert.
    :return: corresponding native python object.
    """

    too = type(dbus_object)
    handler = {
        dbus.Dictionary:
            lambda x:
            {dbus_object_parser(key): dbus_object_parser(x[key]) for key in x},
        dbus.Array: lambda x: [dbus_object_parser(y) for y in list(x)],
        dbus.Boolean: bool,
        dbus.Double: float,
        dbus.Int16: int,
        dbus.Int32: int,
        dbus.Int64: int,
        dbus.UInt16: int,
        dbus.UInt32: int,
        dbus.UInt64: int,
        dbus.String: str,
        dbus.Signature: str,
        dbus.ObjectPath: str,
        dbus.Byte: bytes,
    }.get(too, None)
    if handler is None:
        raise ValueError('DBus type provided not supported: ' + str(too))
    elif handler is bytes:
        return handler([dbus_object])
    return handler(dbus_object)
