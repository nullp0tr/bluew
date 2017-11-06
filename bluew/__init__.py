"""
Bluew: A Bluetooth Library.

Bluew a simplified bluetooth library for python,
with a clear and easy API, which was heavily influenced
by the Requests HTTP library.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from .api import pair, info, trust
from .api import write_attribute, read_attribute
from .api import Connection


__all__ = ['pair',
           'info',
           'trust',
           'write_attribute',
           'read_attribute',
           'Connection']
