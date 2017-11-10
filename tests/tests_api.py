"""
bluew.tests
~~~~~~~~~~~

This module provides tests for the Bluew API.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""

import bluew
from bluew.connections import BluewConnectionError
import bluew.responses as resps
from bluew.plugables import UsedEngine
from unittest import TestCase
from testconfig import config
from nose.plugins.attrib import attr


@attr('req_engine')
class APITeststWithoutDev(TestCase):
    """Tests for the Bluew API without a device available"""

    def test_pair(self):
        """Test pair without device available."""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(BluewConnectionError,
                          bluew.pair, mac=mac)

    def test_info(self):
        """Test info without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(BluewConnectionError,
                          bluew.info, mac=mac)

    def test_trust(self):
        """Test trust without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(BluewConnectionError,
                          bluew.trust, mac=mac)

    def test_read_attribute(self):
        """Test read_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(BluewConnectionError,
                          bluew.read_attribute,
                          mac=mac, attribute='x')

    def test_write_attribute(self):
        """Test write_attribute without device available"""

        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(BluewConnectionError,
                          bluew.write_attribute,
                          mac=mac, attribute='x',
                          data='0x00')

    def test_connection_error(self):
        """Test the exception thrown when device is not available"""

        try:
            bluew.pair('xx')
        except BluewConnectionError as exp:
            error = "Bluew was not able to connect to device."
            self.assertEqual(error, str(exp))


@attr('req_engine')
@attr('req_dev')
class APITestsWithDev(TestCase):
    """Tests for the Bluew API with a device available"""

    def test_pair(self):
        """Test pair with device available."""

        mac = config['dev']['testdev1']['mac']
        resp = bluew.pair(mac)
        self.assertTrue(resp.has_succeeded)
        self.assertEqual(resp, resps.PairSucceededResponse())
        resp = bluew.pair(mac)
        self.assertEqual(resp, resps.PairedAlreadyResponse())

    def test_trust(self):
        """Test trust with device available."""

        mac = config['dev']['testdev1']['mac']
        resp = bluew.trust(mac)
        self.assertTrue(resp.has_succeeded)
        self.assertEqual(resp, resps.TrustSucceededResponse())
        resp = bluew.trust(mac)
        self.assertEqual(resp, resps.TrustedAlreadyResponse())

    def test_info(self):
        """Test info with device available."""

        mac = config['dev']['testdev1']['mac']
        resp = bluew.info(mac)
        self.assertTrue(resp.has_succeeded)
        self.assertTrue(isinstance(resp, resps.InfoSucceededResponse))

    def test_read_attribute(self):
        """Test read_attribute with device available."""

        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        resp = bluew.read_attribute(mac, attribute)
        self.assertTrue(resp.has_succeeded)
        self.assertTrue(isinstance(resp, resps.ReadSucceededResponse))

    def test_write_attribute(self):
        """Test write_attribute with device available."""

        mac = config['dev']['testdev1']['mac']
        attribute = config['dev']['testdev1']['correct_attribute']
        resp = bluew.write_attribute(mac, attribute, '0x03 0x01 0x01')
        self.assertTrue(resp.has_succeeded)
        self.assertEqual(resp, resps.WriteSucceededResponse())


@attr('req_engine')
class ResponseTestWithoutDev(TestCase):
    """Test (**)FailedResponses."""

    def test_connect_resp(self):
        """Test ConnectFailedResponse."""

        engine = UsedEngine()
        mac = 'xx:xx:xx:xx:xx'
        resp = engine.connect(mac)
        self.assertEqual(resp, resps.ConnectFailedResponse())

    def test_disconnect_resp(self):
        """Test DisconnectFailedResponses."""

        engine = UsedEngine()
        mac = 'xx:xx:xx:xx:xx'
        resp = engine.disconnect(mac)
        self.assertEqual(resp, resps.DisconnectFailedResponse())

    def test_pair_resp(self):
        """Test PairFailedResponses."""

        engine = UsedEngine()
        mac = 'xx:xx:xx:xx:xx'
        resp = engine.pair(mac)
        self.assertEqual(resp, resps.PairFailedResponse())

    def test_trust_resp(self):
        """Test TrustFailedResponses."""

        engine = UsedEngine()
        mac = 'xx:xx:xx:xx:xx'
        resp = engine.trust(mac)
        self.assertEqual(resp, resps.TrustFailedResponse())

    def test_info_resp(self):
        """Test InfoFailedResponses."""

        engine = UsedEngine()
        mac = 'xx:xx:xx:xx:xx'
        resp = engine.info(mac)
        self.assertEqual(resp, resps.InfoFailedResponse())

    def test_read_attr_resp(self):
        """Test ReadFailedResponses."""

        engine = UsedEngine()
        mac = 'xx:xx:xx:xx:xx'
        resp = engine.read_attribute(mac, 'aa')
        self.assertEqual(resp, resps.ReadFailedResponse())

    def test_write_attr_resp(self):
        """Test WritetFailedResponses."""

        engine = UsedEngine()
        mac = 'xx:xx:xx:xx:xx'
        resp = engine.write_attribute(mac, 'xx', '0x01')
        self.assertEqual(resp, resps.WriteFailedResponse())


@attr('req_engine')
@attr('req_dev')
class ResponseTestWithDev(TestCase):
    """Test ConnectSucceededResponse and DisconnectSucceededResponse"""

    def test_connect_resp(self):
        """Test ConnectSucceededResponse"""

        engine = UsedEngine()
        mac = config['dev']['testdev1']['mac']
        resp = engine.connect(mac)
        self.assertEqual(resp, resps.ConnectSucceededResponse())
        resp = engine.connect(mac)
        self.assertEqual(resp, resps.ConnectedAlreadyResponse())

    def test_disconnect_resp(self):
        """Test DisconnectSucceededResponse"""

        engine = UsedEngine()
        mac = config['dev']['testdev1']['mac']
        resp = engine.disconnect(mac)
        self.assertEqual(resp, resps.DisconnectSucceededResponse())
        resp = engine.disconnect(mac)
        self.assertEqual(resp, resps.DisconnectedAlreadyResponse())
