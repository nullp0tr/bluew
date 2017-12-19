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
from bluew.engine import EngineBluewError


@attr('req_engine')
class APITeststWithoutDev(TestCase):
    """Tests for the Bluew API without a device available"""

    def test_pair(self):
        """Test pair without device available."""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError,
                          bluew.pair, mac=mac)

    def test_info(self):
        """Test info without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError,
                          bluew.info, mac=mac)

    def test_trust(self):
        """Test trust without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError,
                          bluew.trust, mac=mac)

    def test_read_attribute(self):
        """Test read_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError,
                          bluew.read_attribute,
                          mac=mac, attribute='x')

    def test_write_attribute(self):
        """Test write_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError,
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

    @attr('here')
    def test_write_attribute(self):
        """Test write_attribute with device available."""

        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        resp = bluew.write_attribute(mac, attribute, [0x03, 0x01, 0x01])
        self.assertTrue(resp)

    def test_get_devices(self):
        """Test write_attribute with device available."""

        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        resp = bluew.get_devices()
        self.assertTrue(resp)


@attr('req_engine')
@attr('req_dev')
class ResponseTestWithDev(TestCase):
    """Test ConnectSucceededResponse and DisconnectSucceededResponse"""

    def test_connect_resp(self):
        """Test ConnectSucceededResponse"""

        engine = UsedEngine()
        mac = config['dev']['testdev1']['mac']
        engine.disconnect(mac)
        resp = engine.connect(mac)
        self.assertTrue(resp)

    def test_disconnect_resp(self):
        """Test DisconnectSucceededResponse"""

        engine = UsedEngine()
        mac = config['dev']['testdev1']['mac']
        engine.connect(mac)
        resp = engine.disconnect(mac)
        self.assertTrue(resp)


@attr('req_engine')
@attr('req_dev')
@attr('cnct')
class ConnectionTestWithDev(TestCase):

    def test_connection(self):
        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        with bluew.Connection(mac) as connection:
            connection.trust()
            print('pairing: ')
            print(connection.pair())
            connection.read_attribute(attribute)
            connection.write_attribute(attribute, [0x03, 0x01, 0x01])