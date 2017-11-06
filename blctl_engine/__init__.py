"""
blctl_engine
~~~~~~~~~~~~~~~~~~~

This module provides a default engine for bluew,
BlctlEngine which basically just wraps Bluetoothctl
from Bluez +5.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from .engine import BlctlEngine


__all__ = ['BlctlEngine']
