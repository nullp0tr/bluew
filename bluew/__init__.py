"""
Bluew: A Bluetooth Library.

Bluew a simplified bluetooth library for python,
with a clear and easy API, which was heavily influenced
by the Requests HTTP library.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from .api import connect, disconnect, remove
from .api import pair, info, trust, distrust
from .api import write_attribute, read_attribute
from .api import Connection, get_devices
from .devices import Device
from .controllers import Controller
from .errors import DeviceNotAvailable

__all__ = ['connect',
           'disconnect',
           'pair',
           'remove',
           'info',
           'trust',
           'distrust',
           'write_attribute',
           'read_attribute',
           'Connection',
           'DeviceNotAvailable',
           'get_devices',
           'Device',
           'Controller']
