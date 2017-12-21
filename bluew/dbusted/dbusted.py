"""
bluew.dbusted
~~~~~~~~~~~~

This modlule contains an implementation of an EngineBluew class,
using the bluez D-Bus API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


import threading
import time

from dbus.mainloop.glib import DBusGMainLoop

from bluew.dbusted.interfaces import *

from bluew.engine import EngineBluew

from bluew.dbusted.decorators import *

from gi.repository import GLib


class DBusted(EngineBluew):
    """
    DBusted is an EngineBluew implementation, Using the Bluez D-Bus API.
    """

    __instance = None
    __loop = None
    __thread = None
    __bus = None
    __count = 0

    def __new__(cls, *args, **kwargs):
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
        version = "0.0.6"
        kwargs['name'] = name
        kwargs['version'] = version
        super().__init__(*args, **kwargs)
        self.cntrl = kwargs.get('cntrl', None)
        self._bus = DBusted.__bus
        self._init_cntrl()

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
                pass

    def _init_cntrl(self):
        if self.cntrl is None:
            controllers = self.get_controllers()
            if len(controllers) == 0:
                raise Exception('Fuck!')
            cntrl = controllers[0].Path.replace('/org/bluez/', '')
            self.cntrl = cntrl

    @mac_to_dev
    @check_availablity
    def connect(self, dev):
        deviface = BluezDeviceInterface(self._bus, dev, self.cntrl)
        deviface.connect_device()
        return True

    @mac_to_dev
    @check_if_connected
    @check_availablity
    def disconnect(self, dev):
        deviface = BluezDeviceInterface(self._bus, dev, self.cntrl)
        deviface.disconnect_device()
        return True

    @mac_to_dev
    @check_availablity
    @check_if_paired
    def pair(self, dev):
        deviface = BluezDeviceInterface(self._bus, dev, self.cntrl)
        deviface.pair_device()
        paired = self.is_device_paired(dev)
        return paired

    @mac_to_dev
    # @check_availablity
    def remove(self, dev):
        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.remove_device(dev)
        return True

    def start_engine(self):
        self._register_agent()

    def _register_agent(self):
        amiface = BluezAgentManagerInterface(self._bus)
        return amiface.register_agent()

    def stop_engine(self):
        self._unregister_agent()
        DBusted.__count -= 1
        if not DBusted.__count:
            DBusted.__loop.quit()
            DBusted.__instance = None
            DBusted.__loop = None
            DBusted.__thread = None
            DBusted.__bus = None

    def _unregister_agent(self):
        amiface = BluezAgentManagerInterface(self._bus)
        return amiface.unregister_agent()

    def get_controllers(self):
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_controllers()

    def get_devices(self):
        self.start_scan()
        boiface = BluezObjectInterface(self._bus)
        devices = self._timeout(boiface.get_devices, 5)()
        self.stop_scan()
        return devices

    @mac_to_dev
    def get_services(self, dev):
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_services(dev)

    @mac_to_dev
    def get_characteristics(self, dev):
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_characteristics(dev)

    def is_device_available(self, dev):
        devices = self.get_devices()
        for device in devices:
            if dev in device.Path:
                return True
        return False

    def is_device_paired(self, dev, timeout=5):
        paired = False
        start_time = time.time()
        timed_out = lambda: time.time() > start_time + timeout
        while (paired is False) and (timed_out() is False):
            devices = self.get_devices()
            for device in devices:
                if dev in device.Path:
                    paired = device.Paired
        return paired

    def is_device_connected(self, dev):
        devices = self.get_devices()
        for device in devices:
            connected = device.Connected
            if dev in device.Path and connected:
                return True
        return False

    def __uuid_to_path(self, uuid, dev):
        chars = self.get_characteristics(dev)
        for char in chars:
            if uuid == char.UUID:
                return char.Path

    def _uuid_to_path(self, uuid, dev, timeout=10):
        start_time = time.time()
        timed_out = lambda: time.time() > start_time + timeout
        path = ''
        while not path and not timed_out():
            chars = self.get_characteristics(dev)
            try:
                char = list(filter(lambda char: uuid == char.UUID, chars))[0]
                path = char.Path
            except IndexError:
                pass
        print(path)
        return path

    @mac_to_dev
    @check_availablity
    def info(self, dev):
        devices = self.get_devices()
        device = list(filter(lambda x: dev in x.Path, devices))[0]
        return device

    @mac_to_dev
    @check_availablity
    def trust(self, dev):
        deviface = BluezDeviceInterface(self._bus, dev, self.cntrl)
        deviface.trust_device()
        return True

    @mac_to_dev
    @check_availablity
    def untrust(self, dev):
        deviface = BluezDeviceInterface(self._bus, dev, self.cntrl)
        deviface.untrust_device()
        return True

    def start_scan(self):
        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.start_discovery()
        return True

    def stop_scan(self):
        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.stop_discovery()
        return True

    @mac_to_dev
    @check_availablity
    def read_attribute(self, dev, uuid):
        path = self._uuid_to_path(uuid, dev)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        return dbus_object_parser(gattchrciface.read_value())

    @mac_to_dev
    @check_availablity
    def write_attribute(self, dev, uuid, data):
        path = self._uuid_to_path(uuid, dev)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        gattchrciface.write_value(data)
        return True

    @mac_to_dev
    @check_availablity
    def notify(self, dev, uuid, handler):
        path = self._uuid_to_path(uuid, dev)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        handler = self._handle_notification(handler)
        gattchrciface.start_notify(handler)
        return

    @mac_to_dev
    @check_availablity
    def stop_notify(self, dev, uuid):
        path = self._uuid_to_path(uuid, dev)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        gattchrciface.stop_notify()
        return

    @staticmethod
    def _handle_notification(func):
        def wrapper(*args):
            try:
                data = bytes(args[1][dbus.String('Value')])
                return func(data)
            except KeyError:
                pass
        return wrapper

    @staticmethod
    def _timeout(func, timeout):
        def wrapper(*args, **kwargs):
            result = False
            start_time = time.time()
            current_time = time.time()
            while (current_time < start_time + timeout) and not result:
                result = func(*args, **kwargs)
                current_time = time.time()
            return result
        return wrapper
