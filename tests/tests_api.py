"""
bluew.tests
~~~~~~~~~~~

This module provides tests for the Bluew API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

import bluew
from unittest import TestCase
from testconfig import config
from nose.plugins.attrib import attr
from bluew.errors import DeviceNotAvailable, ControllerSpecifiedNotFound


@attr('req_engine')
class APITeststWithoutDev(TestCase):
    """Tests for the Bluew API without a device available"""

    def test_connect(self):
        """Test connect without device available."""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.connect, mac=mac, timeout=0)

    def test_disconnect(self):
        """Test disconnect without device available."""

        mac = 'xx:xx:xx:xx:xx'
        bluew.disconnect(mac, timeout=0)

    def test_pair(self):
        """Test pair without device available."""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.pair, mac=mac, timeout=0)

    def test_info(self):
        """Test info without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.info, mac=mac, timeout=0)

    def test_trust(self):
        """Test trust without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.trust, mac=mac, timeout=0)

    def test_distrust(self):
        """Test distrust without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.distrust, mac=mac, timeout=0)

    def test_read_attribute(self):
        """Test read_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.read_attribute,
                          mac=mac, attribute='x', timeout=0)

    def test_write_attribute(self):
        """Test write_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.write_attribute,
                          mac=mac, attribute='x',
                          data='0x00', timeout=0)


@attr('req_engine')
@attr('req_dev')
class APITestsWithDev(TestCase):
    """Tests for the Bluew API with a device available"""

    def test_connect_disconnect(self):
        """Test connect & disconnect with device available."""

        mac = config['dev']['testdev1']['mac']
        bluew.connect(mac)
        bluew.disconnect(mac)

    def test_pair(self):
        """Test pair with device available."""

        mac = config['dev']['testdev1']['mac']
        bluew.pair(mac)
        paired = bluew.info(mac).Paired
        self.assertTrue(paired)

    def test_trust(self):
        """Test trust with device available."""

        mac = config['dev']['testdev1']['mac']
        bluew.trust(mac)
        trusted = bluew.info(mac).Trusted
        self.assertTrue(trusted)

    def test_distrust(self):
        """Test distrust with device available."""

        mac = config['dev']['testdev1']['mac']
        bluew.distrust(mac)
        trusted = bluew.info(mac).Trusted
        self.assertFalse(trusted)

    def test_info(self):
        """Test info with device available."""

        mac = config['dev']['testdev1']['mac']
        resp = bluew.info(mac)
        self.assertTrue(resp)
        self.assertIsInstance(resp, bluew.Device)
        self.assertEqual(mac, resp.Address)

    def test_read_attribute(self):
        """Test read_attribute with device available."""

        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        resp = bluew.read_attribute(mac, attribute)
        self.assertTrue(resp)

    def test_write_attribute(self):
        """Test write_attribute with device available."""

        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        bluew.write_attribute(mac, attribute, [0x03, 0x01, 0x01])

    @attr('notify')
    def test_notify(self):
        """Test notify with device available."""

        mac = config['dev']['testdev1']['mac']
        n_attribute = config['dev']['testdev1']['notify_attribute']
        con = bluew.Connection(mac)
        con.notify(n_attribute, lambda data: True)
        con.stop_notify(n_attribute)
        con.close()

    def test_get_devices(self):
        """Test get_devices with device available."""

        mac = config['dev']['testdev1']['mac']
        devices = bluew.get_devices()
        self.assertTrue(devices)
        has_device = (mac == dev.Address for dev in devices)
        has_device = list(filter(lambda x: x is True, has_device))
        self.assertTrue(has_device)


@attr('req_engine')
@attr('req_dev')
@attr('cnct')
class ConnectionTestWithDev(TestCase):
    """Test a Connection object with device available."""

    def test_connection(self):
        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        cntrl = config['dev']['testcntrl']
        with bluew.Connection(mac, cntrl=cntrl) as connection:
            connection.trust()
            connection.pair(d_init=True)
            chrcs = connection.chrcs
            has_atr = bool(filter(lambda chrc: chrc.UUID == attribute, chrcs))
            self.assertTrue(has_atr)
            srvs = connection.services
            has_atr = bool(filter(lambda srv: srv.UUID == attribute, srvs))
            self.assertTrue(has_atr)
            connection.read_attribute(attribute)
            data = [0x03, 0x01, 0x01]
            connection.write_attribute(attribute, data)
            attr = connection.read_attribute(attribute)
            data = [bytes([val]) for val in data]
            self.assertEqual(attr[:len(data)], data)


@attr('req_engine')
@attr('cnct')
class ConnectionTestWithWrongContrller(TestCase):
    """Test a Connection with wrong controller."""

    def test_connection(self):
        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        cntrl = 'hci666'
        self.assertRaises(ControllerSpecifiedNotFound,
                          bluew.Connection,
                          mac, cntrl=cntrl)
