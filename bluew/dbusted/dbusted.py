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


class DBusted(EngineBluew):

    __instance = None
    __loop = None
    __thread = None

    def __new__(cls, *args, **kwargs):
        if DBusted.__instance is None:
            from gi.repository import GLib
            DBusted.__instance = object.__new__(cls)
            DBusted.__loop = DBusGMainLoop(set_as_default=True)
            DBusted.__loop = GLib.MainLoop()
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
        # self._bus = dbus.SystemBus(mainloop=DBusted.__loop)
        self._bus = dbus.SystemBus()
        self._init_cntrl()

    @staticmethod
    def _start_loop():
        DBusted.__loop.run()

    def _init_cntrl(self):
        if self.cntrl is None:
            controllers = self.get_controllers()
            if len(controllers) == 0:
                raise Exception('Fuck!')
            cntrl = controllers[0].Path.replace('/org/bluez/', '')
            self.cntrl = cntrl

    def _register_agent(self):
        amiface = BluezAgentManagerInterface(self._bus)
        return amiface.register_agent()

    def _unregister_agent(self):
        amiface = BluezAgentManagerInterface(self._bus)
        return amiface.unregister_agent()

    def get_controllers(self):
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_controllers()

    def get_devices(self):
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_devices()

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

    def is_device_paired(self, dev, timeout=10):
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

    def _uuid_to_path(self, uuid, dev):
        chars = self.get_characteristics(dev)
        for char in chars:
            if uuid == char.UUID:
                return char.Path

    @mac_to_dev
    def info(self, dev):
        devices = self.get_devices()
        device = list(filter(lambda x: dev in x.Path, devices))[0]
        return device

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
        #thread = threading.Thread(target=deviface.pair_device)
        #thread = threading.Thread(target=lambda: print('lol'))
        #thread.start()
        # return paired
        deviface.pair_device()
        paired = self.is_device_paired(dev)
        return paired

    @mac_to_dev
    def remove(self, dev):
        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.remove_device(dev)
        return True

    @mac_to_dev
    def trust(self, dev):
        deviface = BluezDeviceInterface(self._bus, dev, self.cntrl)
        deviface.trust_device()
        return True

    @mac_to_dev
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
    def notify(self, dev, uuid, handler):
        path = self._uuid_to_path(uuid, dev)
        gattchrciface = BluezGattCharInterface(self._bus, path)
        gattchrciface.start_notify(handler)
        return


    def _get_device_or_timeout(self, dev, timeout=20):
        self.start_scan()
        print('hi')
        available = self.is_device_available(dev)
        start_time = time.time()

        def _timedout():
            return time.time() > start_time + timeout

        while not available and not _timedout():
            available = self.is_device_available(dev)
        self.stop_scan()
        return available
