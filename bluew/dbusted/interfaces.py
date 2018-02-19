"""
bluew.dbusted.interfaces
~~~~~~~~~~~~~~~~~

This module provides D-Bus interfaces provided by the bluez API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""
import logging

from typing import Tuple, List, Callable  # pylint: disable=W0611
from dbus.connection import SignalMatch  # pylint: disable=W0611

import dbus

from bluew.characteristics import BLECharacteristic
from bluew.controller import Controller
from bluew.dbusted.utils import dbus_object_parser
from bluew.device import Device
from bluew.services import BLEService


BLUEZ_SERVICE_NAME = 'org.bluez'
BLUEZ_SERVICE_PATH = '/org/bluez/'

DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
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

DBUS_NO_REPLY_ERR = 'org.freedesktop.DBus.Error.NoReply'
DBUS_UNKNOWN_OBJ_ERR = 'org.freedesktop.DBus.Error.UnknownObject'


def get_exp_name_msg(exp: dbus.DBusException) -> Tuple[str, str]:
    """Get name and message of DBusException."""
    return exp.get_dbus_name(), exp.get_dbus_message()


def error_is(exp: dbus.DBusException, string: str) -> bool:
    """Check if error name or message is a specific string."""
    name, msg = get_exp_name_msg(exp)
    return name == string or msg == string


def pp_error(exp: dbus.DBusException) -> str:
    """This returns a nicely formatted str of the error, for logging."""
    name, msg = get_exp_name_msg(exp)
    ret = "handling::{name}::with_message::{msg}".format(name=name, msg=msg)
    return ret


def log_iface_error(iface: str, exp: dbus.DBusException) -> None:
    """This logs the errors handled."""
    logger = logging.getLogger(__name__)
    error = pp_error(exp)
    record = 'DBusted::Interface:{}:'.format(iface) + error
    logger.debug(record)


class BluezAdapterInterface(object):
    """Bluez D-Bus Adapter interface."""

    ADAPTER_IFACE = 'org.bluez.Adapter1'

    def __init__(self, bus, controller):
        self.cntrl = controller
        bluez_obj = bus.get_object(BLUEZ_SERVICE_NAME,
                                   BLUEZ_SERVICE_PATH + self.cntrl)
        self.manager = dbus.Interface(bluez_obj, ADAPTER_IFACE)

    def start_discovery(self) -> None:
        """StartDiscovery() method on org.bluez.Adapter1 Interface."""

        try:
            self.manager.StartDiscovery()
        except dbus.DBusException as exp:
            self._handle_start_discovery_error(exp)

    @staticmethod
    def _handle_start_discovery_error(exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_OAIP):
            # ERROR: org.bluez.Error.Failed && org.bluez.Error.InProgress
            # If already scanning we got no business turning on scanning
            # again.
            return

        elif error_is(exp, bzerr.BLUEZ_NOT_READY_ERR):
            # ERROR: org.bluez.Error.NotReady
            # This error get's thrown when the bluetooth adapter/controller
            # is not ready for action, aka not turned on.
            raise bzerr(bzerr.BLUEZ_NOT_READY_ERR)

        else:
            raise exp

    def stop_discovery(self) -> None:
        """StopDiscovery() method on org.bluez.Adapter1 Interface."""

        try:
            self.manager.StopDiscovery()
        except dbus.DBusException as exp:
            self._handle_stop_disovery_error(exp)

    @staticmethod
    def _handle_stop_disovery_error(exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_NO_DISCOV_STARTED):
            # ERROR: org.bluez.Error.Failed
            # This error get's thrown with this message when we're trying
            # to stop discovery before even starting it.
            return

        elif error_is(exp, bzerr.BLUEZ_NOT_READY_ERR):
            # ERROR: org.bluez.Error.NotReady
            # This the usual adapter/controller not ready, aka not turned on,
            # at least in most cases.
            raise bzerr(bzerr.BLUEZ_NOT_READY_ERR)

        elif error_is(exp, bzerr.BLUEZ_NOT_AUTHORIZED_ERR):
            # ERROR: org.bluez.Error.NotAuthorized
            # From what I can tell from the bluez source code, this error
            # doesn't get thrown from this method. But you never really know!
            raise bzerr(bzerr.BLUEZ_NOT_AUTHORIZED_ERR)

        else:
            raise exp

    def remove_device(self, dev: str) -> None:
        """RemoveDevice() method on org.bluez.Adapter1 Interface."""

        try:
            self.manager.RemoveDevice(BLUEZ_SERVICE_PATH + self.cntrl + dev)
        except dbus.DBusException as exp:
            self._handle_remove_device_error(exp)

    @staticmethod
    def _handle_remove_device_error(exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        if error_is(exp, bzerr.BLUEZ_DOES_NOT_EXIST_ERR):
            # ERROR: org.Bluez.DoesNotExist
            # Device does not exist and thus doesn't need to be removed.
            return

        elif error_is(exp, bzerr.BLUEZ_INVALID_ARGUMENTS_ERR):
            # ERROR: org.bluez.Error.InvalidArguments
            # Device argument is probably wrong, or more or less than needed
            # arguments were passed.
            raise bzerr(bzerr.BLUEZ_INVALID_ARGUMENTS_ERR)

        elif error_is(exp, bzerr.BLUEZ_NOT_READY_ERR):
            # ERROR: org.bluez.Error.NotReady
            # Adapter or controller is not ready, aka turned off, or not even
            # available.
            raise bzerr(bzerr.BLUEZ_NOT_READY_ERR)

        else:
            raise exp


class BluezDeviceInterface(object):
    """Bluez D-Bus device interface: org.bluez.Device1"""

    DEVICE_IFACE = 'org.bluez.Device1'

    def __init__(self, bus, dev, controller):
        self.bus = bus
        self.cntrl = controller
        self.dev = dev
        bluez_obj = bus.get_object(BLUEZ_SERVICE_NAME,
                                   BLUEZ_SERVICE_PATH + self.cntrl + self.dev)
        self.manager = dbus.Interface(bluez_obj, DEVICE_IFACE)
        self.prop_manager = dbus.Interface(bluez_obj, DBUS_PROP_IFACE)
        self.logger = logging.getLogger(__name__)

    def connect_device(self) -> None:
        """Connect() method on org.bluez.Device1 Interface."""

        try:
            self.manager.Connect()
        except dbus.DBusException as exp:
            self._handle_connect_error(exp)

    def _handle_connect_error(self, exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_OAIP):
            # ERROR: org.bluez.Error.Failed
            # Here we only handle Error.Failed when the message
            # says the the operation is already in progress.
            self._err_connect_retry()

        elif error_is(exp, bzerr.BLUEZ_IN_PROGRESS_ERR):
            # ERROR: org.bluez.Error.InProgress
            # This is another OAIP error, but it get's thrown from
            # a different function in bluez, and this time as a real
            # Error.InProgress and not masked as Error.Failed.
            self._err_connect_retry()

        elif error_is(exp, bzerr.BLUEZ_ALREADY_CONNECTED_ERR):
            # ERROR: org.bluez.Error.AlreadyConnected
            # Well if the device is already connected then just return;
            # Objective achieved. Don't get suprised by segfaults if you
            # call this a 100 times though.
            return

        elif error_is(exp, bzerr.BLUEZ_NOT_READY_ERR):
            # ERROR: org.bluez.Error.NotReady
            # Not ready means that the bluetooth controller is either
            # disabled or not ready for action.
            raise bzerr(bzerr.BLUEZ_NOT_READY_ERR)

        elif error_is(exp, bzerr.DBUS_NO_REPLY_ERR):
            # ERROR: org.freedesktop.DBus.Error.NoReply
            # The most likely reason for this error right now is the device
            # not being available, so check for availability beforehand.
            raise bzerr(bzerr.UNKNOWN_ERROR)

        else:
            raise exp

    def _err_connect_retry(self) -> None:
        self.disconnect_device()
        self.connect_device()

    def disconnect_device(self) -> None:
        """Disconnect() method on org.bluez.Device1 Interface."""

        try:
            self.manager.Disconnect()
        except dbus.DBusException as exp:
            self._handle_disconnect_error(exp)

    @staticmethod
    def _handle_disconnect_error(exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_NOT_CONNECTED):
            # ERROR: org.bluez.Error.Failed
            # This error get's thrown when the device, we're trying to
            # disconnect from is not even connected.
            return
        elif error_is(exp, bzerr.BLUEZ_NOT_CONNECTED_ERR):
            # ERROR: org.bluez.Error.NotConnected
            # This error also get's thrown when the device we're trying
            # to disconnect from is not available, different part that
            # throws this in bluez -> different signature :scratchhead:.
            return
        else:
            raise exp

    def pair_device(self) -> None:
        """Pair() method on org.bluez.Device1 Interface."""

        self.manager.Pair(reply_handler=lambda *args, **kwargs: None,
                          error_handler=lambda *args: None)

    @staticmethod
    def _handle_pair_error(exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        if error_is(exp, bzerr.BLUEZ_AUTH_CANCELLED_ERR):
            # ERROR: org.bluez.Error.AuthenticationCanceled
            # Since we haven't implemented CancelPairing, the only logical
            # cause for this error is the device disappearing amidst pairing.
            # we'll throw not connected error.
            raise bzerr(bzerr.BLUEZ_NOT_CONNECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_ALREADY_EXISTS_ERR):
            # ERROR: org.bluez.Error.AlreadyExists
            # This isn't really an error, this just tells us that the device
            # is already paired.
            return

        elif error_is(exp, bzerr.BLUEZ_INVALID_ARGUMENTS_ERR):
            # ERROR: org.bluez.Error.InvalidArguments
            # This should never happen as long as nobody passes
            # manager.Pair() an argument other than reply_handler &
            # error_handler.
            raise bzerr(bzerr.BLUEZ_INVALID_ARGUMENTS_ERR)

        elif error_is(exp, bzerr.BLUEZ_FAILED_ERR):
            # ERROR: org.bluez.Error.Failed
            # Can be caused by an error during connection, like when a device
            # is not around, or by an error during the bonding because another
            # device is pairing, Don't be ambiguous check for availability
            # beforehand, so you *MIGHT* assume that another device is paring.
            raise bzerr(bzerr.BLUEZ_FAILED_ERR)

        elif error_is(exp, bzerr.BLUEZ_CONN_ATTEMPT_FAILED_ERR):
            # ERROR: org.bluez.Error.ConnectionAttemptFailed
            # This is caused when the connection attempt before pairing
            # fails. Connect before pairing to avoid this one. We'll throw
            # not connected error instead, so that you can try connecting,
            # and find the problem with it.
            raise bzerr(bzerr.BLUEZ_NOT_CONNECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_AUTH_FAILED_ERR):
            # ERROR: org.bluez.Error.AuthenticationFailed
            # This is caused when the authentication with the device
            # fails with no clear reason.
            raise bzerr(bzerr.BLUEZ_AUTH_FAILED_ERR)

        elif error_is(exp, bzerr.BLUEZ_AUTH_REJECTED_ERR):
            # ERROR: org.bluez.Error.AuthenticationRejected.
            # The device doesn't wanna authenticate, what can we do?
            raise bzerr(bzerr.BLUEZ_AUTH_REJECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_AUTH_TIMEOUT_ERR):
            # ERROR: org.bluez.Error.AuthenticationTimeout.
            # The authentication didn't succeed in time.
            raise bzerr(bzerr.BLUEZ_AUTH_TIMEOUT_ERR)

        elif error_is(exp, bzerr.DBUS_NO_REPLY_ERR):
            # ERROR: org.freedesktop.DBus.Error.NoReply
            # D-Bus times out some times before bluez sends a reply
            # and sometimes even though the pairing has already suceeded
            # before the timeout, this error still get's raised.
            return

        else:
            raise exp

    def trust_device(self) -> None:
        """Change Trusted property to True"""
        self.prop_manager.Set(DEVICE_IFACE, 'Trusted', True)

    def distrust_device(self) -> None:
        """Changed Trusted property to False"""
        self.prop_manager.Set(DEVICE_IFACE, 'Trusted', False)


class BluezGattCharInterface(object):
    """Bluez D-Bus GattCharacteristic Interface"""

    __SIGNALS = []  # type: List[Tuple[SignalMatch, str]]
    __IFACE = 'org.bluez.GattCharacteristic1'

    def __init__(self, bus, path):
        self.bus = bus
        bluez_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, path)
        self.manager = dbus.Interface(bluez_obj, self.__IFACE)
        self.path = path
        self.logger = logging.getLogger(__name__)

    def read_value(self) -> dbus.Array:
        """ReadValue() method on org.bluez.GattCharacteristic1 Interface."""

        try:
            return self.manager.ReadValue({})
        except dbus.DBusException as exp:
            self._handle_read_value_error(exp)

    def _handle_read_value_error(self, exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        log_iface_error(self.__IFACE, exp)
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_NOT_CONNECTED):
            # ERROR: org.bluez.Error.Failed
            # Bluez throws an Error.Failed with a 'Not connected' message,
            # when the device is well... not connected. Just always connect
            # before hand, so you know this error occurred because the device
            # disappeared.
            raise bzerr(bzerr.BLUEZ_NOT_CONNECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_ERR_MSG_FTSRR):
            # ERROR: org.bluez.Error.Failed
            # Bluez also throws an Error.Failed with a different message;
            # 'Failed to send read request'. The details of how this can
            # happen are wait too long for a comment.
            raise bzerr(bzerr.UNKNOWN_ERROR)

        elif error_is(exp, bzerr.BLUEZ_IN_PROGRESS_ERR):
            # ERROR: org.bluez.Error.InProgress
            # You shouldn't be reading an attribute before another read is
            # done. If the attribute is volatile and changing, use notify
            # instead.
            raise bzerr(bzerr.BLUEZ_IN_PROGRESS_ERR)

        elif error_is(exp, bzerr.BLUEZ_ERR_MSG_NOT_PAIRED):
            # ERROR: org.bluez.Error.NotPermitted
            # This is NotPermitted error comes with the message, 'Not paired'
            # which means that you need authentication to read/write the
            # specified attribute.
            raise bzerr(bzerr.NOT_PAIRED)

        elif error_is(exp, bzerr.BLUEZ_NOT_PERMITTED_ERR):
            # ERROR: org.bluez.Error.NotPermitted
            # This error get's thrown when you're trying to read an attribute
            # you shouldn't be trying to READ!
            raise bzerr(bzerr.BLUEZ_NOT_PERMITTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_NOT_AUTHORIZED_ERR):
            # ERROR: org.bluez.Error.NotAuthorized
            # This error means you can't read this attribute without
            # pairing.
            raise bzerr(bzerr.BLUEZ_NOT_AUTHORIZED_ERR)

        elif error_is(exp, bzerr.BLUEZ_NOT_SUPPORTED_ERR):
            # ERROR: org.bluez.Error.NotSupported
            # This error means that the OpCode of the attribute is not
            # supported by the server.
            raise bzerr(bzerr.BLUEZ_NOT_SUPPORTED_ERR)

        else:
            raise exp

    def write_value(self, data: List[int]) -> None:
        """WriteValue() method on org.bluez.GattCharacteristic1 Interface."""

        try:
            self.manager.WriteValue(data, {})
        except dbus.DBusException as exp:
            self._handle_write_value_error(exp)

    def _handle_write_value_error(self, exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        log_iface_error(self.__IFACE, exp)
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_NOT_CONNECTED):
            # ERROR: org.bluez.Error.Failed
            # Bluez throws an Error.Failed with a 'Not connected' message,
            # when the device is well... not connected. Just always connect
            # before hand, so you know this error occurred because the device
            # disappeared.
            raise bzerr(bzerr.BLUEZ_NOT_CONNECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_ERR_MSG_NO_ATT):
            # ERROR: org.bluez.Error.Failed
            # Can be caused by a host of things, but can also be caused by
            # the device disappearing during write.
            raise bzerr(bzerr.BLUEZ_NOT_CONNECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_ERR_MSG_FTIW):
            # ERROR: org.bluez.Error.Failed
            # This one here happens *I THINK* when a wrong option flag
            # is passed to WriteValue.
            raise bzerr(bzerr.BLUEZ_FAILED_ERR)

        elif error_is(exp, bzerr.BLUEZ_IN_PROGRESS_ERR):
            # ERROR: org.bluez.Error.InProgress
            # You shouldn't be writing again during a write operation.
            raise bzerr(bzerr.BLUEZ_IN_PROGRESS_ERR)

        elif error_is(exp, bzerr.BLUEZ_ERR_MSG_NOT_PAIRED):
            # ERROR: org.bluez.Error.NotPermitted
            # This is NotPermitted error comes with the message, 'Not paired'
            # which means that you need authentication to read/write the
            # specified attribute.
            raise bzerr(bzerr.NOT_PAIRED)

        elif error_is(exp, bzerr.BLUEZ_NOT_PERMITTED_ERR):
            # ERROR: org.bluez.Error.NotPermitted
            # This error get's thrown when the fd is already acquired on
            # this attribute by client (others??).
            raise bzerr(bzerr.BLUEZ_NOT_PERMITTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_NOT_AUTHORIZED_ERR):
            # ERROR: org.bluez.Error.NotAuthorized
            # This error means you can't write this attribute without
            # pairing.
            raise bzerr(bzerr.BLUEZ_NOT_AUTHORIZED_ERR)

        elif error_is(exp, bzerr.BLUEZ_NOT_SUPPORTED_ERR):
            # ERROR: org.bluez.Error.NotSupported
            # This error means that the OpCode of the attribute is not
            # supported by the server.
            raise bzerr(bzerr.BLUEZ_NOT_SUPPORTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_INVALID_VAL_LEN):
            # ERROR: org.bluez.Error.InvalidValueLength
            # The data list passed is too long or too short, most likely too
            # long for the attribute.
            raise bzerr(bzerr.BLUEZ_INVALID_VAL_LEN)

        else:
            raise exp

    def start_notify(self, handler: Callable) -> None:
        """StartNotify() method on org.bluez.GattCharacteristic1 Interface."""

        try:
            self.manager.StartNotify()
        except dbus.DBusException as exp:
            self._handle_start_notify_error(exp)
        else:
            self._add_signal(handler)

    def _add_signal(self, handler: Callable) -> None:
        if not self._sig_already_registered():
            sig = self.bus.add_signal_receiver(handler, path=self.path)
            self.__SIGNALS.append((sig, self.path))

    def _sig_already_registered(self) -> bool:
        for _, path in self.__SIGNALS:
            if path == self.path:
                return True
        return False

    def _handle_start_notify_error(self, exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        log_iface_error(self.__IFACE, exp)
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_FANS):
            # ERROR: org.bluez.Error.Failed
            # Error.Failed with message "Failed allocate notify session".
            # This means a failure during allocating a notify session for
            # our client. This error is the result of a d-bus error, like
            # the message sender not being assigned.
            raise bzerr(bzerr.UNKNOWN_ERROR)

        elif error_is(exp, bzerr.BLUEZ_IN_PROGRESS_ERR):
            # ERROR: org.bluez.Error.InProgress
            # This is the result of trying to register another notification,
            # when there's one already and the device is not connected.
            raise bzerr(bzerr.BLUEZ_NOT_CONNECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_ERR_MSG_FRNS):
            # ERROR: org.bluez.Error.Failed
            # Error.Failed with message "Failed to register notify session".
            # This means that the device is not connected.
            raise bzerr(bzerr.BLUEZ_NOT_CONNECTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_ERR_MSG_ALREADY_NOTIFYING):
            # ERROR: org.bluez.Error.Failed
            # This error means that we're already notifying on this specific
            # attribute.
            return

        elif error_is(exp, bzerr.BLUEZ_NOT_PERMITTED_ERR):
            # ERROR: org.bluez.Error.NotPermitted
            # This error means that notify for this attribute is already
            # acquired by this client (others??).
            raise bzerr(bzerr.BLUEZ_NOT_PERMITTED_ERR)

        elif error_is(exp, bzerr.BLUEZ_NOT_SUPPORTED_ERR):
            # ERROR: org.bluez.Error.NotSupported
            # This error means that the attribute doesn't support notifying.
            raise bzerr(bzerr.BLUEZ_NOT_SUPPORTED_ERR)

        else:
            raise exp

    def stop_notify(self) -> None:
        """StopNotify() method on org.bluez.GattCharacteristic1 Interface."""

        try:
            self.manager.StopNotify()
        except dbus.DBusException as exp:
            self._handle_stop_notify_error(exp)
        else:
            self._remove_signal()

    def _remove_signal(self) -> None:
        signals = []
        for signal, path in BluezGattCharInterface.__SIGNALS:
            if path == self.path:
                signal.remove()
            else:
                signals.append((signal, path))
        BluezGattCharInterface.__SIGNALS = signals

    def _handle_stop_notify_error(self, exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        log_iface_error(self.__IFACE, exp)
        if error_is(exp, bzerr.BLUEZ_ERR_MSG_NO_NOTIFY):
            # ERROR: org.bluez.Error.Failed
            # When we get this error with the message "No notify session
            # started" we can just return as if the operation has succeeded.
            return


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
        adapters = tuple(map(lambda obj: Controller(**obj), objects))
        return adapters

    def get_devices(self):
        """THIS IS NOT AT THE CORRECT LEVEL OF ABSTRACTION."""
        objects = self._get_objects('org.bluez.Device1')
        devices = tuple(map(lambda obj: Device(**obj), objects))
        return devices

    def get_services(self, dev):
        """THIS IS NOT AT THE CORRECT LEVEL OF ABSTRACTION."""
        objects = self._get_objects('org.bluez.GattService1')
        objects = list(filter(lambda x: dev in x.get('Path', None), objects))
        services = tuple(map(lambda obj: BLEService(**obj), objects))
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

    __IFACE = 'org.bluez.AgentManager1'

    def __init__(self, bus):
        self.bus = bus
        bluez_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")
        self.manager = dbus.Interface(bluez_obj, self.__IFACE)
        self.agent_path = '/org/bluez/bluew'
        self.agent_cap = ''

    def register_agent(self) -> None:
        """RegisterAgent() method on interface org.bluez.AgentManager1"""

        try:
            self.manager.RegisterAgent(self.agent_path, self.agent_cap)
        except dbus.DBusException as exp:
            self._handle_register_agent_error(exp)

    def _handle_register_agent_error(self, exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        log_iface_error(self.__IFACE, exp)
        if error_is(exp, bzerr.BLUEZ_INVALID_ARGUMENTS_ERR):
            # Error: org.bluez.Error.InvalidArguments
            # This exception means you passed wrong capabilities, or a wrong
            # path to RegisterAgent(), we'll just raise the same exception,
            # since right now that's not configurable. and it would only
            # get raised if we refactor this incorrectly, hence we should
            # actually see the exception!!!
            raise exp

        elif error_is(exp, bzerr.BLUEZ_ALREADY_EXISTS_ERR):
            # ERROR: org.bluez.Error.AlreadyExists"
            # DBusted should take care of not trying to register more than one
            # agent at a time, as soon as we want it to run from different
            # interpreter instances at the same time, we should make the path
            # dynamic. Once again raise to see it while refactoring.
            raise exp

        else:
            raise exp

    def unregister_agent(self) -> None:
        """Possible errors: org.bluez.Error.DoesNotExist"""

        try:
            self.manager.UnregisterAgent(self.agent_path)
        except dbus.DBusException as exp:
            self._handle_unregister_agent_error(exp)

    def _handle_unregister_agent_error(self, exp: dbus.DBusException) -> None:
        bzerr = BluezInterfaceError
        log_iface_error(self.__IFACE, exp)
        if error_is(exp, bzerr.BLUEZ_DOES_NOT_EXIST_ERR):
            # ERROR: org.bluez.Error.DoesNotExist
            # The agent we're trying to unregister doesn't exist, this should
            # not be caused, if caused, we just raise again cause it signals
            # a bug in DBusted, since it tried to unregister an agent, that
            # is not registered.
            raise exp


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


class BluezInterfaceError(Exception):
    """
    BluezInterfaceError get's raised when the interface,
    has no way of solving the problem, and delegates it instead to
    the DBusted.
    """
    BLUEZ_ERR = 'org.bluez.Error.'
    BLUEZ_FAILED_ERR = BLUEZ_ERR + 'Failed'
    BLUEZ_ALREADY_CONNECTED_ERR = BLUEZ_ERR + 'AlreadyConnected'
    BLUEZ_DOES_NOT_EXIST_ERR = BLUEZ_ERR + 'DoesNotExist'
    BLUEZ_IN_PROGRESS_ERR = BLUEZ_ERR + 'InProgress'
    BLUEZ_NOT_READY_ERR = BLUEZ_ERR + 'NotReady'
    BLUEZ_AGENT_NOT_AVAILABLE_ERR = BLUEZ_ERR + 'AgentNotAvailable'
    BLUEZ_NO_SUCH_ADAPTER_ERR = BLUEZ_ERR + 'NoSuchAdapter'
    BLUEZ_NOT_PERMITTED_ERR = BLUEZ_ERR + 'NotPermitted'
    BLUEZ_NOT_AUTHORIZED_ERR = BLUEZ_ERR + 'NotAuthorized'
    BLUEZ_NOT_AVAILABLE_ERR = BLUEZ_ERR + 'NotAvailable'
    BLUEZ_NOT_CONNECTED_ERR = BLUEZ_ERR + 'NotConnected'
    BLUEZ_NOT_SUPPORTED_ERR = BLUEZ_ERR + 'NotSupported'
    BLUEZ_ALREADY_EXISTS_ERR = BLUEZ_ERR + 'AlreadyExists'
    BLUEZ_INVALID_ARGUMENTS_ERR = BLUEZ_ERR + 'InvalidArguments'
    BLUEZ_AUTH_CANCELLED_ERR = BLUEZ_ERR + 'AuthenticationCanceled'
    BLUEZ_CONN_ATTEMPT_FAILED_ERR = BLUEZ_ERR + 'ConnectionAttemptFailed'
    BLUEZ_AUTH_FAILED_ERR = BLUEZ_ERR + 'AuthenticationFailed'
    BLUEZ_AUTH_REJECTED_ERR = BLUEZ_ERR + 'AuthenticationRejected'
    BLUEZ_AUTH_TIMEOUT_ERR = BLUEZ_ERR + 'AuthenticationTimeout'
    BLUEZ_INVALID_VAL_LEN = BLUEZ_ERR + 'InvalidValueLength'

    BLUEZ_ERR_MSG_OAIP = 'Operation already in progress'
    BLUEZ_ERR_MSG_NOT_PAIRED = 'Not paired'
    BLUEZ_ERR_MSG_NO_ATT = 'No ATT transport'
    BLUEZ_ERR_MSG_NOT_CONNECTED = 'Not connected'
    BLUEZ_ERR_MSG_FTIW = 'Failed to initiate write'
    BLUEZ_ERR_MSG_FANS = 'Failed allocate notify session'
    BLUEZ_ERR_MSG_FRNS = 'Failed to register notify session'
    BLUEZ_ERR_MSG_ALREADY_NOTIFYING = 'Already notifying'
    BLUEZ_ERR_MSG_NO_NOTIFY = 'No notify session started'
    BLUEZ_ERR_MSG_NO_DISCOV_STARTED = 'No discovery started'
    BLUEZ_ERR_MSG_FTSRR = 'Failed to send read request'

    DBUS_NO_REPLY_ERR = 'org.freedesktop.DBus.Error.NoReply'
    DBUS_UNKNOWN_OBJ_ERR = 'org.freedesktop.DBus.Error.UnknownObject'

    UNKNOWN_ERROR = 'UnknownError.'
    DBUS_CONNECTION_ERROR = 'DBusConnectionError'
    NOT_PAIRED = 'NotPaired'

    def __init__(self, error_name):
        super().__init__()
        self.error_name = error_name
