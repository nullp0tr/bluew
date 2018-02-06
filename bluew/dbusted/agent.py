"""
bluew.dbusted.agent
~~~~~~~~~~~~~~~~~~~

This module implements a pairing agent for dbusted.

:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


import dbus


AGENT_INTERFACE = 'org.bluez.Agent1'


# noinspection PyPep8Naming
# pylint: disable=C0103
class Agent(dbus.service.Object):
    """Pairing agent for bluez D-Bus API."""

    exit_on_release = True

    def __init__(self, *args, passkey='', pincode='', **kwargs):
        super().__init__(*args, **kwargs)
        self.passkey = passkey
        self.pincode = pincode

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self) -> None:
        """
        This method gets called when the service daemon unregisters the agent.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device: str) -> str:
        """
        This method gets called when the service daemon needs to get the
        passkey for an authentication.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device: str, pincode: str) -> None:
        """
        This method gets called when the service daemon needs to display a
        pincode for an authentication.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device: str) -> dbus.UInt32:
        """
        This method gets called when the service daemon needs to get the
        passkey for an authentication.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device: str, passkey: dbus.UInt32,
                       entered: dbus.UInt16) -> None:
        """
        This method gets called when the service daemon needs to get the
        passkey for an authentication.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def RequestConfirmation(self, device: str, passkey: dbus.UInt32) -> None:
        """
        This method gets called when the service daemon needs to confirm a
        passkey for an authentication.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device: str) -> None:
        """
        This method gets called to request the user to authorize an incoming
        pairing attempt which would in other circumstances trigger the
        just-works model.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device: str, uuid: str) -> None:
        """
        This method gets called when the service daemon needs to authorize a
        connection/service request.
        """
        pass

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self) -> None:
        """
        This method gets called to indicate that the agent request failed
        before a reply was returned.
        """
        pass
