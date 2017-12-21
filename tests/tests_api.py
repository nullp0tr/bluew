"""
bluew.tests
~~~~~~~~~~~

This module provides tests for the Bluew API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

import bluew
from bluew.plugables import UsedEngine
from unittest import TestCase
from testconfig import config
from nose.plugins.attrib import attr
from bluew.errors import DeviceNotAvailable


@attr('req_engine')
class APITeststWithoutDev(TestCase):
    """Tests for the Bluew API without a device available"""

    def test_pair(self):
        """Test pair without device available."""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.pair, mac=mac)

    def test_info(self):
        """Test info without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.info, mac=mac)

    def test_trust(self):
        """Test trust without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.trust, mac=mac)

    def test_read_attribute(self):
        """Test read_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.read_attribute,
                          mac=mac, attribute='x')

    def test_write_attribute(self):
        """Test write_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(DeviceNotAvailable,
                          bluew.write_attribute,
                          mac=mac, attribute='x',
                          data='0x00')


@attr('req_engine')
@attr('req_dev')
class APITestsWithDev(TestCase):
    """Tests for the Bluew API with a device available"""

    def test_pair(self):
        """Test pair with device available."""

        mac = config['dev']['testdev1']['mac']
        resp = bluew.pair(mac)
        self.assertTrue(resp)

    def test_trust(self):
        """Test trust with device available."""

        mac = config['dev']['testdev1']['mac']
        resp = bluew.trust(mac)
        self.assertTrue(resp)

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
        self.assertIsInstance(resp, list)

    def test_write_attribute(self):
        """Test write_attribute with device available."""

        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        resp = bluew.write_attribute(mac, attribute, [0x03, 0x01, 0x01])
        self.assertTrue(resp)

    def test_get_devices(self):
        """Test get_devices with device available."""

        mac = config['dev']['testdev1']['mac']
        devices = bluew.get_devices()
        has_device = (mac == dev.Address for dev in devices)
        has_device = list(filter(lambda x: x is True, has_device))
        self.assertTrue(has_device)


@attr('req_engine')
@attr('req_dev')
@attr('cnct')
class ConnectionTestWithDev(TestCase):

    def test_connection(self):
        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        with bluew.Connection(mac) as connection:
            connection.trust()
            connection.pair()
            connection.read_attribute(attribute)
            data = [0x03, 0x01, 0x01]
            connection.write_attribute(attribute, data)
            attr = connection.read_attribute(attribute)
            data = [bytes([val]) for val in data]
            self.assertEqual(attr[:len(data)], data)
