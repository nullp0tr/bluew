"""
bluew.tests
~~~~~~~~~~~

This module provides tests for the BluewEngine class.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from unittest import TestCase
from bluew.engine import EngineBluew, EngineBluewError
from nose.plugins.attrib import attr


@attr('req_engine')
class ValidationTest(TestCase):
    """Tests validation functions for bluew.BluewEngine."""

    def test_name_fails(self):
        """Test that BluewEngine validates the name."""

        try:
            EngineBluew()
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.NAME_NOT_SET)
        else:
            self.assertFalse(True)

    def test_version_fails(self):
        """Test that BluewEngine validates the version."""

        try:
            EngineBluew(name='test')
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.VERSION_NOT_SET)
        else:
            self.assertFalse(True)

    def test_engine_error(self):
        """Test EngineBluewError."""

        try:
            EngineBluew()
        except EngineBluewError as exp:
            self.assertEqual(str(exp), exp.reason)


@attr('req_engine')
class APICallsTest(TestCase):
    """Tests that the api calls raise an exception when not overridden."""

    def test_connect(self):
        """Test connect"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError, engine.connect, mac=mac)

        try:
            engine.connect(mac)
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.NOT_IMPLEMENTED)

    def test_disconnect(self):
        """Test disconnect"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError, engine.disconnect, mac=mac)

        try:
            engine.disconnect(mac)
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.NOT_IMPLEMENTED)

    def test_pair(self):
        """Test pair"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError, engine.pair, mac=mac)

        try:
            engine.pair(mac)
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.NOT_IMPLEMENTED)

    def test_trust(self):
        """Test trust"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError, engine.trust, mac=mac)

        try:
            engine.trust(mac)
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.NOT_IMPLEMENTED)

    def test_read_attribute(self):
        """Test read_attribute"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError,
                          engine.read_attribute,
                          mac=mac, attribute='x')

        try:
            engine.read_attribute(mac, 'x')
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.NOT_IMPLEMENTED)

    def test_write_attribute(self):
        """Test read_attribute"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineBluewError,
                          engine.write_attribute,
                          mac=mac, attribute='x', data='0x00')

        try:
            engine.write_attribute(mac, 'x', '0x00')
        except EngineBluewError as exp:
            self.assertEqual(exp.reason, EngineBluewError.NOT_IMPLEMENTED)
