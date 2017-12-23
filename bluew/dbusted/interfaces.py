"""
bluew.dbusted.interfaces
~~~~~~~~~~~~~~~~~

This module provides D-Bus interfaces provided by the bluez API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

from typing import Tuple, List  # pylint: disable=W0611
from dbus.connection import SignalMatch  # pylint: disable=W0611

import dbus

from bluew.characteristics import BLECharacteristic
from bluew.controllers import Controller
from bluew.dbusted.utils import dbus_object_parser
from bluew.devices import Device
from bluew.services import BLEService


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
        except dbus.DBusException as exp:
            err_msg = exp.get_dbus_message()
            in_progress = err_msg == BLUEZ_IN_PROGRESS_ERROR_OAIP
            if in_progress:
                return True
            else:
                raise exp
        return True

    def stop_discovery(self):
        # TODO: HANDLE FOLLOWING ERRORS
        """Possible errors: org.bluez.Error.NotReady
                            org.bluez.Error.Failed
                            org.bluez.Error.NotAuthorized"""
        try:
            self.manager.StopDiscovery()
        except dbus.DBusException as exp:
            err_msg = exp.get_dbus_message()
            not_scanning = err_msg == 'No discovery started'
            if not_scanning:
                return True
            else:
                raise exp
        return True

    def remove_device(self, dev):
        # TODO: HANDLE FOLLOWING ERROS
        """Possible errors:
                            org.Bluez.DoesNotExist: Does Not Exist
                            org.bluez.Error.InvalidArguments
                            org.bluez.Error.Failed"""
        try:
            self.manager.RemoveDevice(BLUEZ_SERVICE_PATH + self.cntrl + dev)
        except dbus.DBusException as exp:
            e_dbus_name = exp.get_dbus_name()
            e_dbus_msg = exp.get_dbus_message()
            does_not_exist_error = e_dbus_name == BLUEZ_DOES_NOT_EXIST_ERROR
            does_not_exist_msg = e_dbus_msg == BLUEZ_DOES_NOT_EXIST_ERROR_DNE
            if does_not_exist_error and does_not_exist_msg:
                return True
            else:
                raise exp
        return True


class BluezDeviceInterface(object):
    """Bluez D-Bus device interface."""

    DEVICE_IFACE = 'org.bluez.Device1'

    def __init__(self, bus, dev, controller):
        self.bus = bus
        self.cntrl = controller
        self.dev = dev
        bluez_obj = bus.get_object(BLUEZ_SERVICE_NAME,
                                   BLUEZ_SERVICE_PATH + self.cntrl + self.dev)
        self.manager = dbus.Interface(bluez_obj, DEVICE_IFACE)
        self.prop_manager = dbus.Interface(bluez_obj, DBUS_PROP_IFACE)

    def connect_device(self):
        # TODO : HANDLE FOLLOWING ERRORS
        """Possible errors:
                            org.bluez.Error.NotReady
                            org.bluez.Error.Failed
                            org.bluez.Error.InProgress
        """

        try:
            self.manager.Connect()
        except dbus.DBusException as exp:
            self._handle_connection_error(exp)
        return True

    def _handle_connection_error(self, exp):
        e_dbus_name = exp.get_dbus_name()
        e_dbus_msg = exp.get_dbus_message()
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
            raise exp

    def disconnect_device(self):
        # TODO : HANDLE FOLLOWING ERRORS
        """Possible errors: org.bluez.Error.NotConnected"""
        try:
            self.manager.Disconnect()
        except dbus.DBusException as exp:
            e_dbus_name = exp.get_dbus_name()
            e_dbus_msg = exp.get_dbus_message()
            if e_dbus_name == BLUEZ_FAILED_ERROR:
                if e_dbus_msg == BLUEZ_FAILED_NOT_CONNECTED:
                    return True
                else:
                    raise exp
            else:
                raise exp
        return True

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
        self.bus.add_signal_receiver(lambda *args: print('lol'),
                                     interface_keyword='dbus_interface',
                                     member_keyword='member',
                                     path='/org/bluez/bluew')

        def _handle_error(exp):
            # This is a hack because of two errors that bluez raises, even
            # when pairing succeeds. Problem with NoReply is that it takes too
            # long, so we just pass this function to handle the errors, while
            # we're checking if device got paired. If we find that the device
            # is already paired we terminate regardless and return, which
            # sometimes triggers AuthenticationCanceled cause bluez thinks it
            # hasn't succeeded in pairing?
            err = exp.get_dbus_name()
            no_reply = err == 'org.freedesktop.DBus.Error.NoReply'
            auth_cancelled = err == 'org.bluez.Error.AuthenticationCanceled'
            if no_reply or auth_cancelled:
                pass
            else:
                raise exp

        def _handle_reply(*args, **kwargs):
            # pylint: disable=W0612,W0613
            # We don't really need to handle the reply.
            pass

        self.manager.Pair(reply_handler=_handle_reply,
                          error_handler=_handle_error)

    def trust_device(self):
        """Possible Errors: """
        self.prop_manager.Set(DEVICE_IFACE, 'Trusted', True)
        return True

    def untrust_device(self):
        """Possible Errors: """
        self.prop_manager.Set(DEVICE_IFACE, 'Trusted', False)
        return True


class BluezGattCharInterface(object):
    """Bluez D-Bus GattCharacteristic Interface"""

    __SIGNALS = []  # type: List[Tuple[SignalMatch, str]]

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
        options = {'s': 's'}
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

        options = {'s': 's'}
        self.manager.WriteValue(data, options)

    def start_notify(self, handler):
        # TODO: HANDLE FOLLOWING ERRORS
        """Possible Errors:
                            org.bluez.Error.Failed
                            org.bluez.Error.NotPermitted
                            org.bluez.Error.InProgress
                            org.bluez.Error.NotSupported"""

        sig = self.bus.add_signal_receiver(handler, path=self.path)
        BluezGattCharInterface.__SIGNALS.append((sig, self.path))
        return self.manager.StartNotify()

    def stop_notify(self):
        # TODO: FIND POSSIBLE ERROS
        """Possible erros: """

        signals = []
        for sig in BluezGattCharInterface.__SIGNALS:
            if sig[1] == self.path:
                sig[0].remove()
            else:
                signals.append(sig)
        BluezGattCharInterface.__SIGNALS = signals

        return self.manager.StopNotify()


class BluezObjectInterface(object):
    """Bluez D-Bus objects Interface"""

    def __init__(self, bus):
        self.bus = bus
        bluez_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, "/")
        self.manager = dbus.Interface(bluez_obj, DBUS_OM_IFACE)

    def _get_objects(self, iface):
        objects = self.manager.GetManagedObjects().items()
        objects = list(map(lambda x: (x[0], x[1].get(iface, None)), objects))
        objects = list(filter(lambda x: x[1] is not None, objects))
        objects = list(map(lambda x: self._parse(x[1], x[0]), objects))
        return objects

    @staticmethod
    def _parse(obj, path):
        parsed_object = dbus_object_parser(obj)
        parsed_object['Path'] = dbus_object_parser(path)
        return parsed_object

    def get_controllers(self):
        """THIS IS NOT AT THE CORRECT LEVEL OF ABSTRACTION."""
        objects = self._get_objects('org.bluez.Adapter1')
        adapters = tuple(map(lambda object: Controller(**object), objects))
        return adapters

    def get_devices(self):
        """THIS IS NOT AT THE CORRECT LEVEL OF ABSTRACTION."""
        objects = self._get_objects('org.bluez.Device1')
        devices = tuple(map(lambda object: Device(**object), objects))
        return devices

    def get_services(self, dev):
        """THIS IS NOT AT THE CORRECT LEVEL OF ABSTRACTION."""
        objects = self._get_objects('org.bluez.GattService1')
        objects = list(filter(lambda x: dev in x.get('Path', None), objects))
        services = tuple(map(lambda object: BLEService(**object), objects))
        return services

    def get_characteristics(self, dev):
        """THIS IS NOT AT THE CORRECT LEVEL OF ABSTRACTION."""
        objects = self._get_objects('org.bluez.GattCharacteristic1')
        objects = list(filter(lambda x: dev in x.get('Path', None), objects))
        characteristics = tuple(
            map(lambda obj: BLECharacteristic(**obj), objects))
        return characteristics


class BluezAgentManagerInterface(object):
    """Bluez AgentManager interface."""

    def __init__(self, bus):
        self.bus = bus
        bluez_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")
        self.manager = dbus.Interface(bluez_obj, 'org.bluez.AgentManager1')
        self.agent_path = '/org/bluez/bluew'
        self.agent_cap = ''

    def register_agent(self):
        # TODO: FIND POSSIBLE ERRORS
        """Possible errors: """
        self.manager.RegisterAgent(self.agent_path, self.agent_cap)
        return True

    def unregister_agent(self):
        # TODO: FIND POSSIBLE ERRORS
        """Possible errors: """
        self.manager.UnregisterAgent(self.agent_path)
        return True


class BluezHealthManagerInterface(object):
    """To be implemented."""
    pass


class BluezProfileManagerInterface(object):
    """To be implemented."""
    pass


class BluezGattManagerInterface(object):
    """To be implemented."""
    pass


class BluezMediaInterface(object):
    """To be implemented."""
    pass


class BluezNetworkServerInterface(object):
    """To be implemented."""
    pass
