"""
Bluew: A Bluetooth Library.

Bluew a simplified bluetooth library for python,
with a clear and easy API, which was heavily influenced
by the Requests HTTP library.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

import logging
import bluew.errors
from .api import connect, disconnect, remove
from .api import pair, info, trust, distrust
from .api import write_attribute, read_attribute
from .api import Connection, devices, controllers
from .device import Device
from .controller import Controller


__version__ = '0.4.5'


# ~~ For production ~~ #
logging.getLogger(__name__).addHandler(logging.NullHandler())


# ~~ For debugging ~~ #
# logger = logging.getLogger(__name__)
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# logger.setLevel(logging.DEBUG)
# logger.addHandler(handler)


__all__ = ['__version__',
           'connect',
           'disconnect',
           'pair',
           'remove',
           'info',
           'trust',
           'distrust',
           'write_attribute',
           'read_attribute',
           'Connection',
           'devices',
           'controllers',
           'Device',
           'Controller',
           'errors']
