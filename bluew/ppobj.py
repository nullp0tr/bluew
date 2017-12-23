"""
bluew.ppobjs
~~~~~~~~~~~~

This module contains an object with a __str__ that returns
all the object's attributes.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class PPObj(object):
    """Bluetooth device object."""

    def __init__(self, attrs, **kwargs):
        for key, value in kwargs.items():
            if key not in attrs:
                name = self.__class__.__name__
                raise TypeError(
                    '{a} should not have attribute {b}'.format(a=name, b=key))
            setattr(self, key, value)

    def __str__(self):
        result = ''
        for key in self.__dict__:
            result += key + ': ' + str(getattr(self, key)) + '\n'
        return result
