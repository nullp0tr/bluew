"""
bluew.engine
~~~~~~~~~~~~

This modlule contains an abstact EngineBluew class,
that should be inherited by functioning engines.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from typing import Callable, List

from bluew.device import Device
from bluew.controller import Controller
from bluew.services import BLEService
from bluew.characteristics import BLECharacteristic
from bluew.errors import BluewError


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
        raise EngineError(EngineError.NAME_NOT_SET)

    def _validate_version(self):
        if isinstance(self.version, str):
            return
        raise EngineError(EngineError.VERSION_NOT_SET)

    def start_engine(self) -> None:
        """
        This function get's called to init the engine before use.
        :return: None.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def stop_engine(self) -> None:
        """
        This function get's called when the engine is not needed anymore,
        for it to close any resources it's using.
        :return: None.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def connect(self, mac: str) -> None:
        """
        This function get's called by Bluew API to connect to device.
        :param mac: MAC address of device.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def disconnect(self, mac: str) -> None:
        """
        This function get's called by Bluew API to disconnect from a device.
        :param mac: MAC address of device.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def pair(self, mac: str) -> None:
        """
        This function get's called by Bluew API to pair with a device.
        :param mac: MAC address of device.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def trust(self, mac: str) -> None:
        """
        This function get's called by Bluew API to trust a device.
        :param mac: MAC address of device.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def distrust(self, mac: str) -> None:
        """
        This function get's called by Bluew API to remove trust
        from a device.
        :param mac: MAC address of device.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def write_attribute(self, mac: str, attribute: str,
                        data: List[int]) -> None:
        """
        This function get's called by Bluew API to write an attribute
        on a device.
        :param mac: MAC address of device.
        :param attribute: UUID of attribute.
        :param data: List of int values to be written.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def read_attribute(self, mac: str, attribute: str) -> List[bytes]:
        """
        This function get's called by Bluew API to read an attribute
        from a device.
        :param mac: MAC address of device.
        :param attribute: UUID of attribute.
        :return: list of values if succeeded, None otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def info(self, mac: str) -> Device:
        """
        This function get's called by Bluew API to get information about
        a device.
        :param mac: MAC address of device.
        :return: Device object if succeeded, None otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def get_devices(self) -> List[Device]:
        """
        This function get's called by Bluew API to get available devices.
        :return: list of Device objects.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def get_controllers(self) -> List[Controller]:
        """
        This function get's called by Bluew API to get available controllers.
        :return: list of Controller objects.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def get_services(self, mac: str) -> List[BLEService]:
        """
        This function get's called by Bluew API to get available services
        of a BLE device.
        :return: list of BLESerivce objects.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def get_chrcs(self, mac: str) -> List[BLECharacteristic]:
        """
        This function get's called by Bluew API to get availbe characteristics
        of a BLE device.
        :return: list of BLECharacteristic objects.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def notify(self, mac: str, attribute: str, handler: Callable) -> None:
        """
        This function get's called by Bluew API to stop notifying on a
        certain attribute.
        :param mac: MAC adress of device.
        :param attribute: UUID of attribute.
        :param handler: This function get's passed the values returned
        from the attribute in bytes.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def stop_notify(self, mac: str, attribute: str) -> None:
        """
        This function get's called by Bluew API to stop notifying on a
        certain attribute.
        :param mac: MAC adress of device.
        :param attribute: UUID of attribute.
        :return: True if succeeded, False otherwise.
        """
        # pylint: disable=W0612,W0613

        self._raise_not_implemented()

    def _raise_not_implemented(self):
        raise EngineError(
            EngineError.NOT_IMPLEMENTED,
            self.name,
            self.version)


class EngineError(BluewError):
    """For those times when the Engine blows."""

    NOT_IMPLEMENTED = 'Used engine does not implement this function'
    NAME_NOT_SET = 'BluewEngine interface does not provice valid name'
    VERSION_NOT_SET = 'BluewEngine interface does not provicd valid version'
    INIT_ERROR = 'Engine was not properly initialized.'
