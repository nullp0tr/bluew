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

from bluew.errors import (NoControllerAvailable,
                          ControllerSpecifiedNotFound,
                          PairError)

from bluew.engine import EngineBluew

from bluew.dbusted.decorators import (mac_to_dev,
                                      check_if_available,
                                      check_if_connected,
                                      check_if_not_paired)

from gi.repository import GLib


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
        version = "0.3.6"
        kwargs['name'] = name
        kwargs['version'] = version
        super().__init__(*args, **kwargs)
        self.cntrl = kwargs.get('cntrl', None)
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
            raise PairError()

    @mac_to_dev
    # @check_availablity
    def remove(self, mac: str) -> None:
        """
        Overriding EngineBluew's remove method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: True if succeeded, False otherwise..
        """

        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.remove_device(mac)

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

        self._start_scan()
        boiface = BluezObjectInterface(self._bus)
        devices = self._timeout(boiface.get_devices, 10)()
        self._stop_scan()
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
    def info(self, mac):
        """
        Overriding EngineBluew's info method.
        :param mac: Device path. @mac_to_dev takes care of getting the proper
        path from the device's mac address.
        :return: Device object.
        """

        devices = self.get_devices()
        device = list(filter(lambda x: mac in x.Path, devices))[0]
        return device

    @mac_to_dev
    @check_if_available
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

    def _is_device_available(self, dev):
        devices = self.get_devices()
        filtered = list(filter(lambda device: dev in device.Path, devices))
        return bool(filtered)

    def _is_device_paired(self, dev):
        devices = self.get_devices()
        filtered = list(filter(lambda device: dev in device.Path, devices))
        filtered = list(filter(lambda device: device.Paired, filtered))
        return bool(filtered)

    def _is_device_paired_timeout(self, dev, timeout=5):
        paired = self._timeout(self._is_device_paired, timeout)(dev)
        return paired

    def _is_device_connected(self, dev):
        devices = self.get_devices()
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

    def _uuid_to_path(self, uuid, dev, timeout=10):
        return self._timeout(self._get_attr_path, timeout)(uuid, dev)

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
