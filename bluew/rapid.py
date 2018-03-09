"""
bluew.rapid
~~~~~~~~~~~

This module implements the building blocks for creating declarative apis with
bluew.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from typing import Iterable, Callable
from bluew import Connection


class RapidAPI:
    """
    All declarative bluew APIs should inherent from this class.
    """

    def __init__(self, mac: str) -> None:
        self.con = Connection(mac)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Clean up connection.
        """
        self.con.close()


class Read(object):
    """
    This descriptor should be used to declare a readable attribute.
    """
    def __init__(self, uuid: str) -> None:
        self.uuid = uuid

    def __get__(self, instance: RapidAPI, owner: object):
        return instance.con.read_attribute(self.uuid)


class Write:
    """
    This descriptor should be used to declare a function that takes input
    and writes it to an attribute. for example:

        class FooAPI(RapidAPI):
            do_some_bar = Write('UUID_HERE', accept=['valid1', 'valid2'])

        foo_api = FooAPI('xx:xx:xx:xx:xx')
        foo_api.do_some_bar('valid1')  # works!
        foo_api.do_some_bar('notvalid')  # Raises ValueError

    """
    def __init__(self, uuid: str, accept=None) -> None:
        self.uuid = uuid
        self.accept = accept

    def __get__(self, instance: RapidAPI, owner) -> Callable:
        return lambda val: self._write(instance, val)

    def _write(self, instance: RapidAPI, val) -> None:
        if self.accept and val not in self.accept:
            raise ValueError('Valued passed is not valid input.')
        instance.con.write_attribute(self.uuid, val)


class Notify:
    """
    This descriptor should be used to declare a function that takes a callback
    which get's called with notification values.
    """
    def __init__(self, uuids: Iterable[str]) -> None:
        self.uuids = uuids

    def __get__(self, instance: RapidAPI, owner) -> Callable:
        return lambda callback, b=instance: self._notify(b, callback)

    def _notify(self, instance: RapidAPI, callback):
        for uuid in self.uuids:
            instance.con.notify(uuid, callback)
        return lambda binded=instance: self._stop_notify(binded)

    def _stop_notify(self, instance: RapidAPI):
        for uuid in self.uuids:
            instance.con.stop_notify(uuid)
