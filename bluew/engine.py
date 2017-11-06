"""
bluew.engine
~~~~~~~~~~~~

This modlule contains an abstact EngineBluew class,
that should be inherited by functioning engines.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


class EngineBluew(object):
    """Abstract bluetooth engine for Bluew.

    To create a bluetooth engine for the Bluew API,
    you need to inherent this class, and implement
    its public functions.

    The engine must also provide these attributes:
    :param self.name: str: Name for the engine.
    :param self.version: str: Version of engine.
    """

    def __init__(self, *args, **kwargs):
        # pylint: disable=W0612,W0613

        self.name = kwargs.get('name', None)
        self.version = kwargs.get('version', None)
        self._validate()

    def _validate(self):
        self._validate_name()
        self._validate_version()

    def _validate_name(self):
        if isinstance(self.name, str):
            return
        raise EngineBluewError(EngineBluewError.NAME_NOT_SET)

    def _validate_version(self):
        if isinstance(self.version, str):
            return
        raise EngineBluewError(EngineBluewError.VERSION_NOT_SET)

    def connect(self, mac):
        """Template connect function to be overridden."""
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def disconnect(self, mac):
        """Template disconnect function to be overridden."""
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def pair(self, mac):
        """Template pair function to be overridden."""
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def trust(self, mac):
        """Template trust function to be overridden."""
        # pylint: disable=W0612,W0613

    def write_attribute(self, mac, attribute, data):
        """Template write_attribute function to be overridden."""
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def read_attribute(self, mac, attribute):
        """Template read_attribute function to be overridden."""
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def _raise_not_implemented(self):
        raise EngineBluewError(
            EngineBluewError.NOT_IMPLEMENTED,
            self.name,
            self.version)


class EngineBluewError(Exception):
    """For those times when the Engine blows."""

    NOT_IMPLEMENTED = 'Used engine does not implement this function'
    NAME_NOT_SET = 'BluewEngine interface does not provice valid name'
    VERSION_NOT_SET = 'BluewEngine interface does not provicd valid version'
    INIT_ERROR = 'Engine was not initialized.'

    def __init__(self, reason, name='', version=''):
        super().__init__()
        self.engine_name = name
        self.version = version
        self.reason = reason

    def __str__(self):
        return self.reason
