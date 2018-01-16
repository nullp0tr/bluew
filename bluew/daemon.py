"""
bluew.daemon
~~~~~~~~~~~~~~~~~

This module provides a Daemon object that tries its best to keep connections
alive, and has the ability to reproduce certain steps when a reconnection is
needed.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


def daemonize(func):
    """
    A function wrapper that checks daemon flags. This wrapper as it is assumes
    that the calling class has a daemon attribute.
    """
    def _wrapper(self, *args, d_init=False, **kwargs):
        if d_init:
            self.daemon.d_init.append((func, self, args, kwargs))
        return func(self, *args, **kwargs)

    return _wrapper


class Daemon(object):
    """The bluew daemon."""

    def __init__(self):
        self.d_init = []

    def run_init_funcs(self):
        """
        This function iterates through the functions added to d_init, and
        runs them in the same order they were added in.
        """
        for func, self_, args, kwargs in self.d_init:
            func(self_, *args, **kwargs)
