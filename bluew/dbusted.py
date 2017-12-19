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

import dbus
from dbus.mainloop.glib import DBusGMainLoop

from bluew.devices import Device
from bluew.services import BLEService
from bluew.adapters import Adapter
from bluew.characteristics import BLECharacteristic

from bluew.engine import EngineBluew, EngineBluewError

from functools import wraps


BLUEZ_SERVICE_NAME = 'org.bluez'
BLUEZ_SERVICE_PATH = '/org/bluez/'

DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHRC_IFACE = 'org.bluez.GattCharacteristic1'
GATT_DESC_IFACE = 'org.bluez.GattDescriptor1'

ADAPTER_IFACE = 'org.bluez.Adapter1'
DEVICE_IFACE = 'org.bluez.Device1'

BLUEZ_FAILED_ERROR = 'org.bluez.Error.Failed'
BLUEZ_FAILED_ERROR_OAIP = 'Operation already in progress'
BLUEZ_FAILED_ERROR_NO_ATT = 'No ATT transport'
BLUEZ_FAILED_NOT_CONNECTED = 'Not connected'
BLUEZ_ALREADY_CONNECTED_ERROR = 'org.bluez.Error.AlreadyConnected'
BLUEZ_DOES_NOT_EXIST_ERROR = 'org.bluez.Error.DoesNotExist'
BLUEZ_DOES_NOT_EXIST_ERROR_DNE = 'Does Not Exist'
BLUEZ_IN_PROGRESS_ERROR = 'org.bluez.Error.InProgress'
BLUEZ_IN_PROGRESS_ERROR_OAIP = 'Operation already in progress'

DBUS_NO_REPLY_ERROR = 'org.freedesktop.DBus.Error.NoReply'
DBUS_UNKNOWN_OBJ_ERROR = 'org.freedesktop.DBus.Error.UnknownObject'

RESP_SUCCESS = 'succeeded'
RESP_FAILED = 'failed'
RESP_ALREADY = 'already'


def dbus_object_parser(dbus_object):
    too = type(dbus_object)
    handler = {
        dbus.Dictionary: lambda x:
            {dbus_object_parser(key): dbus_object_parser(x[key]) for key in x},
        dbus.Array: lambda x: [dbus_object_parser(y) for y in list(x)],
        dbus.Boolean: bool,
        dbus.Double: float,
        dbus.Int16: int,
        dbus.Int32: int,
        dbus.Int64: int,
        dbus.UInt16: int,
        dbus.UInt32: int,
        dbus.UInt64: int,
        dbus.String: str,
        dbus.Signature: str,
        dbus.ObjectPath: str,
        dbus.Byte: dbus.Byte,
    }.get(too, None)
    if handler is None:
        raise ValueError('DBus type provided not supported: ' + str(too))
    return handler(dbus_object)


class BluezAgentManagerInterface(object):
    pass


class BluezHealthManagerInterface(object):
    pass


class BluezProfileManagerInterface(object):
    pass


class BluezGattManagerInterface(object):
    pass


class BluezMediaInterface(object):
    pass


class BluezNetworkServerInterface(object):
    pass


class BluezAdapterInterface(object):
    """Bluez D-Bus Adapter interface."""

    ADAPTER_IFACE = 'org.bluez.Adapter1'

    def __init__(self, bus, controller='hci0'):
        self.cntrl = controller
        bluez_obj = bus.get_object(BLUEZ_SERVICE_NAME,
                                   BLUEZ_SERVICE_PATH + self.cntrl)
        self.manager = dbus.Interface(bluez_obj, ADAPTER_IFACE)

    def start_discovery(self):
        # TODO: HANDLE FOLLOWING ERRORS
        """Possible errors: org.bluez.Error.NotReady
                            org.bluez.Error.Failed"""
        try:
            self.manager.StartDiscovery()
        except dbus.DBusException as e:
            err_msg = e.get_dbus_message()
            in_progress = err_msg == BLUEZ_IN_PROGRESS_ERROR_OAIP
            if in_progress:
                return True
            else: raise e
        return True

    def stop_discovery(self):
        # TODO: HANDLE FOLLOWING ERRORS
        """Possible errors: org.bluez.Error.NotReady
                            org.bluez.Error.Failed
                            org.bluez.Error.NotAuthorized"""
        try:
            self.manager.StopDiscovery()
        except dbus.DBusException as e:
            err_msg = e.get_dbus_message()
            not_scanning = err_msg == 'No discovery started'
            if not_scanning:
                return True
            else: raise e
        return True

    def remove_device(self, dev):
        # TODO: HANDLE FOLLOWING ERROS
        """Possible errors: 
                            org.Bluez.DoesNotExist: Does Not Exist
                            org.bluez.Error.InvalidArguments
                            org.bluez.Error.Failed"""
        try:
            self.manager.RemoveDevice(BLUEZ_SERVICE_PATH + self.cntrl + dev)
        except dbus.DBusException as e:
            e_dbus_name = e.get_dbus_name()
            e_dbus_msg = e.get_dbus_message()
            does_not_exist_error = e_dbus_name == BLUEZ_DOES_NOT_EXIST_ERROR
            does_not_exist_msg = e_dbus_msg == BLUEZ_DOES_NOT_EXIST_ERROR_DNE
            if does_not_exist_error and does_not_exist_msg:
                return True
            else: raise e
        return True


class BluezDeviceInterface(object):
    """Bluez D-Bus device interface."""

    DEVICE_IFACE = 'org.bluez.Device1'

    def __init__(self, bus, dev, controller):
        self.cntrl = controller
        self.dev = dev
        bluez_obj = bus.get_object(BLUEZ_SERVICE_NAME,
                                   BLUEZ_SERVICE_PATH + self.cntrl + self.dev)
        self.manager = dbus.Interface(bluez_obj, DEVICE_IFACE)

    def connect_device(self):
        # TODO : HANDLE FOLLOWING ERRORS
        """Possible errors: 
                            org.bluez.Error.NotReady
                            org.bluez.Error.Failed                #Sorta handled
                            org.bluez.Error.InProgress            #I
        """

        try:
            self.manager.Connect()
        except dbus.DBusException as e:
            self.handle_connection_error(e)
        return True

    def handle_connection_error(self, e):
        e_dbus_name = e.get_dbus_name()
        e_dbus_msg = e.get_dbus_message()
        bluez_failed = e_dbus_name == BLUEZ_FAILED_ERROR
        bluez_oaip = e_dbus_msg == BLUEZ_FAILED_ERROR_OAIP
        if bluez_failed and bluez_oaip:
            self.disconnect_device()
            self.connect_device()
        elif e_dbus_name == BLUEZ_ALREADY_CONNECTED_ERROR:
            return True
        elif e_dbus_name == DBUS_NO_REPLY_ERROR:
            return False
        else:
            raise e

    def disconnect_device(self):
        # TODO : HANDLE FOLLOWING ERRORS
        """Possible errors: org.bluez.Error.NotConnected"""
        try:
            self.manager.Disconnect()
        except dbus.DBusException as e:
            e_dbus_name = e.get_dbus_name()
            e_dbus_msg = e.get_dbus_message()
            if e_dbus_name == BLUEZ_FAILED_ERROR:
                if e_dbus_msg == BLUEZ_FAILED_NOT_CONNECTED:
                    return True, RESP_ALREADY
                else: raise e
            else: raise e
        return True, RESP_SUCCESS

    def pair_device(self):
        # TODO : HANDLE FOLLOWING ERRORS
        """Possible errors: 
                            org.bluez.Error.InvalidArguments
                            org.bluez.Error.Failed
                            org.bluez.Error.AlreadyExists
                            org.bluez.Error.AuthenticationCanceled
                            org.bluez.Error.AuthenticationFailed
                            org.bluez.Error.AuthenticationRejected
                            org.bluez.Error.AuthenticationTimeout
                            org.bluez.Error.ConnectionAttemptFailed"""

        self.manager.Pair()


class BluezGattCharInterface(object):
    """Bluez D-Bus GattCharacteristic Interface"""

    def __init__(self, bus, path):
        self.bus = bus
        bluez_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, path)
        self.manager = dbus.Interface(bluez_obj, GATT_CHRC_IFACE)
        self.path = path

    def read_value(self):
        # TODO: HANDLE FOLLOWING ERRORS
        """Possible Errors: 
                            org.bluez.Error.Failed
                            org.bluez.Error.InProgress
                            org.bluez.Error.NotPermitted
                            org.bluez.Error.NotAuthorized
                            org.bluez.Error.NotSupported"""
        options = {'s':'s'}
        return self.manager.ReadValue(options)

    def write_value(self, data):
        # TODO: HANDLE FOLLOWING ERRORS
        """Possible Errors: 
                            org.bluez.Error.Failed: Not connected.
                            org.bluez.Error.Failed: No ATT transport.
                            org.bluez.Error.InProgress
                            org.bluez.Error.NotPermitted
                            org.bluez.Error.InvalidValueLength
                            org.bluez.Error.NotAuthorized
                            org.bluez.Error.NotSupported"""

        options = {'s':'s'}
        self.manager.WriteValue(data, options)


    def start_notify(self, handler):
        # TODO: HANDLE FOLLOWING ERRORS
        """Possible Errors: 
                            org.bluez.Error.Failed
                            org.bluez.Error.NotPermitted
                            org.bluez.Error.InProgress
                            org.bluez.Error.NotSupported"""


        self.bus.add_signal_receiver(handler,
                                     interface_keyword='dbus_interface',
                                     member_keyword='member',
                                     path=self.path
                                     )
        return self.manager.StartNotify()


class BluezObjectInterface(object):
    """Bluez D-Bus objects Interface"""

    def __init__(self, bus):
        self.bus = bus
        bluez_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, "/")
        self.manager = dbus.Interface(bluez_obj, DBUS_OM_IFACE)

    def _get_objects(self, iface):
        objects = self.manager.GetManagedObjects()
        is_iface = lambda x: (x[0], x[1].get(iface, None))
        objects = list(map(is_iface, objects.items()))
        objects = list(filter(lambda x: x[1] is not None, objects))
        objects = list(map(lambda x: self._parse(x[1], x[0]), objects))
        return objects


    def _parse(self, obj, path):
        parsed_object = dbus_object_parser(obj)
        parsed_object['Path'] = dbus_object_parser(path)
        return parsed_object

    def get_controllers(self):
        objects = self._get_objects('org.bluez.Adapter1')
        adapters = tuple(map(lambda object: Adapter(**object), objects))
        return adapters


    def get_devices(self):
        objects = self._get_objects('org.bluez.Device1')
        devices = tuple(map(lambda object: Device(**object), objects))
        return devices

    def get_services(self, dev):
        objects = self._get_objects('org.bluez.GattService1')
        objects = list(filter(lambda x: dev in x.get('Path', None), objects))
        services = tuple(map(lambda object: BLEService(**object), objects))
        return services

    def get_characteristics(self, dev):
        objects = self._get_objects('org.bluez.GattCharacteristic1')
        objects = list(filter(lambda x: dev in x.get('Path', None), objects))
        characteristics = tuple(map(lambda object: BLECharacteristic(**object), objects))
        return characteristics


def mac_to_dev(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        dev = '/dev_' + dev.replace(':', '_')
        return func(self, dev, *args, **kwargs)
    return wrapper


def check_availablity(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        available = self._get_device_or_timeout(dev)
        if not available:
            raise EngineBluewError(EngineBluewError.DEVICE_NOT_AVAILABLE)
        return func(self, dev, *args, **kwargs)
    return wrapper


def check_if_paired(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        paired = self.is_device_paired(dev)
        if paired:
            return True
        return func(self, dev, *args, **kwargs)
    return wrapper


def check_if_connected(func):
    @wraps(func)
    def wrapper(self, dev, *args, **kwargs):
        connected = self.is_device_connected(dev)
        if not connected:
            return True
        return func(self, dev, *args, **kwargs)
    return wrapper


class DBusted(EngineBluew):

    __instance = None
    __loop = None
    __thread = None

    def __new__(cls, *args, **kwargs):
        if DBusted.__instance is None:
            DBusted.__instance = object.__new__(cls)
            DBusted.__loop = DBusGMainLoop(set_as_default=True)
            # DBusted.__thread = threading.Thread(target=DBusted._start_loop)
        return DBusted.__instance

    def __init__(self, *args, **kwargs):
        name = "DBusted"
        version = "0.0.6"
        kwargs['name'] = name
        kwargs['version'] = version
        super().__init__(*args, **kwargs)
        self.cntrl = kwargs.get('cntrl', None)
        self._bus = dbus.SystemBus(mainloop=DBusted.__loop)
        self._init_cntrl()

    @staticmethod
    def _start_loop(self):
        DBusted.__loop.run()

    def _init_cntrl(self):
        if self.cntrl is None:
            controllers = self.get_controllers()
            if len(controllers) == 0:
                raise Exception('Fuck!')
            cntrl = controllers[0].Path.replace('/org/bluez/', '')
            self.cntrl = cntrl

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

    # @mac_to_dev
    def get_characteristics(self, dev):
        boiface = BluezObjectInterface(self._bus)
        return boiface.get_characteristics(dev)

    def is_device_available(self, dev):
        devices = self.get_devices()
        for device in devices:
            if dev in device.Path:
                return True
        return False

    def is_device_paired(self, dev):
        devices = self.get_devices()
        for device in devices:
            paired = device.Paired
            if dev in device.Path and paired:
                return True
        return False

    def is_device_connected(self, dev):
        devices = self.get_devices()
        for device in devices:
            connected = device.Connected
            if dev in device.Path and connected:
                return True
        return False

    def _uuid_to_path(self, uuid, dev):
        time.sleep(2)
        chars = self.get_characteristics(dev)
        for char in chars:
            if uuid == char.UUID:
                return char.Path

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
        return True

    @mac_to_dev
    def remove(self, dev):
        adiface = BluezAdapterInterface(self._bus, self.cntrl)
        adiface.remove_device(dev)
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

    def _get_device_or_timeout(self, dev, timeout=3):
        self.start_scan()
        available = self.is_device_available(dev)
        start_time = time.time()

        def _timedout():
            return time.time() > start_time + timeout

        while not available and not _timedout():
            available = self.is_device_available(dev)
        self.stop_scan()
        return available
