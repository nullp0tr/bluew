"""
bluew.dbusted
~~~~~~~~~~~~

This modlule contains an implementation of an EngineBluew class,
using the bluez D-Bus API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

import logging

import threading
import time

from typing import List, Optional, Callable  # pylint: disable=W0611

from dbus.mainloop.glib import DBusGMainLoop
import dbus
from gi.repository import GLib


from bluew.dbusted.interfaces import BluezInterfaceError as IfaceError
from bluew.dbusted.interfaces import (BluezGattCharInterface,
                                      BluezAgentManagerInterface,
                                      BluezObjectInterface,
                                      BluezAdapterInterface,
                                      BluezDeviceInterface,
                                      Controller,
                                      Device,
                                      BLECharacteristic,
                                      BLEService,
                                      dbus_object_parser)

from bluew.errors import (BluewError,
                          NoControllerAvailable,
                          ControllerSpecifiedNotFound,
                          PairError,
                          DeviceNotAvailable,
                          ControllerNotReady,
                          ReadWriteNotifyError,
                          InvalidArgumentsError)

from bluew.engine import EngineBluew

from bluew.dbusted.decorators import (mac_to_dev,
                                      check_if_available,
                                      check_if_connected,
                                      check_if_not_paired,
                                      handle_errors)


class DBusted(EngineBluew):
    """
    DBusted is an EngineBluew implementation, Using the Bluez D-Bus API.
    """

    __instance = None  # type: Optional[DBusted]
    __loop = None  # type: Optional[GLib.MainLoop]
    __thread = None  # type: Optional[threading.Thread]
    __bus = None  # type: Optional[dbus.SystemBus]
    __count = 0

    def __new__(cls, *args, **kwargs):
        # pylint: disable=W0612,W0613
        DBusted.__count += 1
        if DBusted.__instance is None:
            DBusted.__instance = object.__new__(cls)
            DBusGMainLoop(set_as_default=True)
            DBusted.__bus = dbus.SystemBus()
            DBusted.__thread = threading.Thread(target=DBusted._start_loop)
            DBusted.__thread.start()
        return DBusted.__instance

    def __init__(self, *args, **kwargs):
        name = "DBusted"
        version = "0.3.8"
        kwargs['name'] = name
        kwargs['version'] = version
        super().__init__(*args, **kwargs)
        self.cntrl = kwargs.get('cntrl', None)
        self.timeout = kwargs.get('timeout', 5)
        self._bus = DBusted.__bus
        self._init_cntrl()
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        self.start_engine()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_engine()

    @staticmethod
    def _start_loop():
        DBusted.__loop = GLib.MainLoop()
        running = True
        while running:
            try:
                running = False
                DBusted.__loop.run()
            except KeyboardInterrupt:
                running = True

    def _init_cntrl(self):
        controllers = self.get_controllers()
        if self.cntrl is None:
            if not controllers:
                self.stop_engine()
                raise NoControllerAvailable()
            cntrl = self._strip_cntrl_path(controllers[0])
            self.cntrl = cntrl
        else:
            paths = list(map(self._strip_cntrl_path, controllers))
            if self.cntrl not in paths:
                self.stop_engine()
                raise ControllerSpecifiedNotFound()

    @property
    def devices(self):
        """A property to get devices nearby."""
        self._start_scan()
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_devices()

    @property
    def controllers(self):
        """A property to get controllers available."""
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_controllers()

    @staticmethod
    def _strip_cntrl_path(cntrl):
        path = getattr(cntrl, 'Path')
        return path.replace('/org/bluez/', '')

    def start_engine(self) -> None:
        """
        Overriding EngineBluew's start_engine method. This method get's called
        to init the engine. We register here an agent with bluez during the
        initialization. DBusted is a singleton, and so we only need to init
        if it's the first instance of DBusted.
        :return: None.
        """
        if DBusted.__count == 1:
            pass
            # self._register_agent()

    def _register_agent(self):
        amiface = BluezAgentManagerInterface(self._bus)
        return amiface.register_agent()

    def stop_engine(self) -> None:
        """
        Overriding EngineBluew's stop_engine method. This method get's called
        when the engine is not needed any more. Since DBusted is a singleton
        we should only destroy things when all instaces are gone. Otherwise
        the engine should keep on running.
        :return: None.
        """

        DBusted.__count -= 1
        if not DBusted.__count:
            # self._unregister_agent()
            DBusted.__loop.quit()
            DBusted.__instance = None
            DBusted.__loop = None
            DBusted.__thread = None
            DBusted.__bus = None

    def _unregister_agent(self):
        amiface = BluezAgentManagerInterface(self._bus)
        return amiface.unregister_agent()

    @mac_to_dev
    @check_if_available
    @handle_errors
    def connect(self, mac: str) -> None:
        """
        Overriding EngineBluew's connect method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: True if succeeded, False otherwise..
        """

        deviface = BluezDeviceInterface(self._bus, mac, self.cntrl)
        deviface.connect_device()

    @mac_to_dev
    @check_if_connected
    @check_if_available
    @handle_errors
    def disconnect(self, mac: str) -> None:
        """
        Overriding EngineBluew's disconnect method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: True if succeeded, False otherwise..
        """

        deviface = BluezDeviceInterface(self._bus, mac, self.cntrl)
        deviface.disconnect_device()

    @mac_to_dev
    @check_if_available
    @check_if_not_paired
    @handle_errors
    def pair(self, mac: str) -> None:
        """
        Overriding EngineBluew's pair method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: True if succeeded, False otherwise..
        """

        deviface = BluezDeviceInterface(self._bus, mac, self.cntrl)
        deviface.pair_device()
        paired = self._is_device_paired_timeout(mac)
        if not paired:
            raise PairError(self.name, self.version)

    @mac_to_dev
    @handle_errors
    def remove(self, mac: str) -> None:
        """
        Overriding EngineBluew's remove method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: True if succeeded, False otherwise..
        """

        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.remove_device(mac)

    def remove_all(self) -> None:
        """Remove all devices."""
        devices = self._get_devices()
        for dev in devices:
            self.remove(getattr(dev, 'Address'))

    def get_controllers(self) -> List[Controller]:
        """
        Overriding EngineBluew's get_controllers method.
        :return: List of controllers available.
        """

        boiface = BluezObjectInterface(self._bus)
        return boiface.get_controllers()

    def get_devices(self) -> List[Device]:
        """
        Overriding EngineBluew's get_devices method.
        :return: List of devices available.
        """

        self.remove_all()
        self._start_scan()
        get_devices = self._tout(self._get_devices,
                                 self.timeout,
                                 lambda x: False)
        devices = get_devices()
        self._stop_scan()
        return devices

    def _get_devices(self) -> List[Device]:
        boiface = BluezObjectInterface(self._bus)
        devices = boiface.get_devices()
        return devices

    @mac_to_dev
    def get_services(self, mac: str) -> List[BLEService]:
        """
        Overriding EngineBluew's get_services method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: List of BLE services available.
        """

        boiface = BluezObjectInterface(self._bus)
        return boiface.get_services(mac)

    @mac_to_dev
    def get_chrcs(self, mac: str) -> List[BLECharacteristic]:
        """
        Overriding EngineBluew's get_chrcs method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: List of BLE characteristics available.
        """

        boiface = BluezObjectInterface(self._bus)
        return boiface.get_characteristics(mac)

    @mac_to_dev
    @check_if_available
    @handle_errors
    def info(self, mac):
        """
        Overriding EngineBluew's info method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: Device object.
        """

        devices = self._get_devices()
        device = list(filter(lambda x: mac in x.Path, devices))[0]
        return device

    @mac_to_dev
    @check_if_available
    @handle_errors
    def trust(self, mac: str) -> None:
        """
        Overriding EngineBluew's trust method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: True if succeeded, False otherwise..
        """

        deviface = BluezDeviceInterface(self._bus, mac, self.cntrl)
        deviface.trust_device()

    @mac_to_dev
    @check_if_available
    @handle_errors
    def distrust(self, mac: str) -> None:
        """
        Overriding EngineBluew's untrust method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: True if succeeded, False otherwise..
        """

        deviface = BluezDeviceInterface(self._bus, mac, self.cntrl)
        deviface.distrust_device()

    def _start_scan(self) -> None:
        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.start_discovery()

    def _stop_scan(self) -> None:
        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.stop_discovery()

    @mac_to_dev
    @check_if_available
    @handle_errors
    def read_attribute(self, mac: str, attribute: str) -> List[bytes]:
        """
        Overriding EngineBluew's read_attribute method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :param attribute: UUID of the BLE attribute.
        :return: Value of attribute, raise exception otherwise.
        """

        path = self._uuid_to_path(attribute, mac)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        return dbus_object_parser(gattchrciface.read_value())

    @mac_to_dev
    @check_if_available
    @handle_errors
    def write_attribute(self, mac: str, attribute: str,
                        data: List[int]) -> None:
        """
        Overriding EngineBluew's write_attribute method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :param attribute: UUID of the BLE attribute.
        :param data: The data you want to write.
        :return: True if succeeded, False otherwise..
        """

        path = self._uuid_to_path(attribute, mac)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        gattchrciface.write_value(data)

    @mac_to_dev
    @check_if_available
    @handle_errors
    def notify(self, mac: str, attribute: str, handler: Callable) -> None:
        """
        Overriding EngineBluew's trust method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :param attribute: UUID of the BLE attribute.
        :param handler: A callback function with the values returned by the
        notifications.
        :return: True if succeeded, False otherwise..
        """

        path = self._uuid_to_path(attribute, mac)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        handler = self._handle_notification(handler)
        gattchrciface.start_notify(handler)

    @mac_to_dev
    @check_if_available
    @handle_errors
    def stop_notify(self, mac: str, attribute: str) -> None:
        """
        Overriding EngineBluew's trust method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :param attribute: UUID of the BLE attribute.
        :return: True if succeeded, False otherwise..
        """

        path = self._uuid_to_path(attribute, mac)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        gattchrciface.stop_notify()

    def _handle_errors(self, exp: IfaceError, *args, **kwargs) -> None:
        auth_timeout = exp.error_name == IfaceError.BLUEZ_AUTH_TIMEOUT_ERR
        auth_failed = exp.error_name == IfaceError.BLUEZ_AUTH_FAILED_ERR
        auth_rejected = exp.error_name == IfaceError.BLUEZ_AUTH_REJECTED_ERR

        if exp.error_name == IfaceError.BLUEZ_NOT_CONNECTED_ERR:
            self.connect(args[0], **kwargs)

        elif exp.error_name == IfaceError.NOT_PAIRED:
            self.pair(args[0], **kwargs)

        elif exp.error_name == IfaceError.BLUEZ_NOT_SUPPORTED_ERR:
            self.stop_engine()
            not_supported = ReadWriteNotifyError.NOT_SUPPORTED
            raise ReadWriteNotifyError(long_reason=not_supported)

        elif exp.error_name == IfaceError.BLUEZ_NOT_PERMITTED_ERR:
            self.stop_engine()
            not_permitted = ReadWriteNotifyError.NOT_PERMITTED
            raise ReadWriteNotifyError(long_reason=not_permitted)

        elif exp.error_name == IfaceError.BLUEZ_NOT_READY_ERR:
            self.stop_engine()
            raise ControllerNotReady

        elif exp.error_name == IfaceError.BLUEZ_NOT_AUTHORIZED_ERR:
            self.stop_engine()
            not_authorized = ReadWriteNotifyError.NOT_AUTHORIZED
            raise ReadWriteNotifyError(long_reason=not_authorized)

        elif exp.error_name == IfaceError.BLUEZ_INVALID_VAL_LEN:
            self.stop_engine()
            invalid_len = InvalidArgumentsError.INVALID_LEN
            raise InvalidArgumentsError(long_reason=invalid_len)

        elif exp.error_name == IfaceError.UNKNOWN_ERROR:
            raise BluewError(BluewError.UNEXPECTED_ERROR)

        elif exp.error_name == IfaceError.BLUEZ_INVALID_ARGUMENTS_ERR:
            self.stop_engine()
            invalid_args = InvalidArgumentsError.INVALID_ARGS
            raise InvalidArgumentsError(long_reason=invalid_args)

        elif exp.error_name == IfaceError.BLUEZ_IN_PROGRESS_ERR:
            self.stop_engine()
            in_progress = ReadWriteNotifyError.IN_PROGRESS
            raise ReadWriteNotifyError(long_reason=in_progress)

        elif exp.error_name == IfaceError.UNKNOWN_ERROR:
            self.stop_engine()
            raise BluewError(BluewError.UNEXPECTED_ERROR)

        elif auth_failed or auth_timeout or auth_rejected:
            self.stop_engine()
            raise PairError(long_reason=PairError.AUTHENTICATION_ERROR)

    def _is_device_available(self, dev):
        self._start_scan()
        devices = self._tout(self._get_devices,
                             self.timeout,
                             lambda devs: any(dev in d.Path for d in devs))
        devices = devices()
        filtered = list(filter(lambda device: dev in device.Path, devices))
        self._stop_scan()
        return bool(filtered)

    def _is_device_paired(self, dev):

        def _dev_is_paired(devs):
            for _dev in devs:
                if dev in _dev.Path and _dev.Paired:
                    return True
            return False

        devices = self._tout(self._get_devices,
                             self.timeout,
                             _dev_is_paired)()
        filtered = list(filter(lambda device: dev in device.Path, devices))
        filtered = list(filter(lambda device: device.Paired, filtered))
        return bool(filtered)

    def _is_device_paired_timeout(self, dev):
        paired = self._is_device_paired(dev)
        return paired

    def _is_device_connected(self, dev):
        devices = self._tout(self._get_devices,
                             self.timeout,
                             lambda devs: any(dev in d.Path for d in devs))
        devices = devices()
        filtered = list(filter(lambda device: dev in device.Path, devices))
        filtered = list(filter(lambda device: device.Connected, filtered))
        return bool(filtered)

    def _get_attr_path(self, uuid, dev):
        chrcs = self.get_chrcs(dev)
        try:
            chrc = list(filter(lambda chrc_: uuid == chrc_.UUID, chrcs))[0]
            path = getattr(chrc, 'Path')  # just silencing pycharm.
        except IndexError:
            path = ''
        return path

    def _uuid_to_path(self, uuid, dev):
        path = self._timeout(self._get_attr_path, self.timeout)(uuid, dev)
        if not path:
            raise DeviceNotAvailable(self.name, self.version)
        return path

    @staticmethod
    def _handle_notification(func):
        def _wrapper(*args):
            try:
                data = bytes(args[1][dbus.String('Value')])
                return func(data)
            except KeyError:
                pass
        return _wrapper

    @staticmethod
    def _timeout(func, timeout):
        def _wrapper(*args, **kwargs):
            result = False
            start_time = time.time()
            current_time = time.time()
            while (current_time < start_time + timeout) and not result:
                result = func(*args, **kwargs)
                current_time = time.time()
            return result
        return _wrapper

    @staticmethod
    def _tout(func, timeout, case):
        def _wrapper(*args, **kwargs):
            is_case = False
            timedout = False
            ret = None
            start_time = time.time()
            while not timedout and not is_case:
                ret = func(*args, **kwargs)
                is_case = case(ret)
                timedout = time.time() > start_time + timeout
            return ret
        return _wrapper
