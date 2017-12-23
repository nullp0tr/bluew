"""
bluew.tests
~~~~~~~~~~~

This module provides tests for the BluewEngine class.


:copyright: (c) 2017 by Ahmed Alsharif.
:license: MIT, see LICENSE for more details.
"""


from unittest import TestCase
from bluew.engine import EngineBluew, EngineError
from nose.plugins.attrib import attr


@attr('req_engine')
class ValidationTest(TestCase):
    """Tests validation functions for bluew.BluewEngine."""

    def test_name_fails(self):
        """Test that BluewEngine validates the name."""

        try:
            EngineBluew()
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.NAME_NOT_SET)
        else:
            self.assertFalse(True)

    def test_version_fails(self):
        """Test that BluewEngine validates the version."""

        try:
            EngineBluew(name='test')
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.VERSION_NOT_SET)
        else:
            self.assertFalse(True)


@attr('req_engine')
class APICallsTest(TestCase):
    """Tests that the api calls raise an exception when not overridden."""

    def test_connect(self):
        """Test connect"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineError, engine.connect, mac=mac)

        try:
            engine.connect(mac)
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.NOT_IMPLEMENTED)

    def test_disconnect(self):
        """Test disconnect"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineError, engine.disconnect, mac=mac)

        try:
            engine.disconnect(mac)
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.NOT_IMPLEMENTED)

    def test_pair(self):
        """Test pair"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineError, engine.pair, mac=mac)

        try:
            engine.pair(mac)
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.NOT_IMPLEMENTED)

    def test_trust(self):
        """Test trust"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineError, engine.trust, mac=mac)

        try:
            engine.trust(mac)
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.NOT_IMPLEMENTED)

    def test_read_attribute(self):
        """Test read_attribute"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineError,
                          engine.read_attribute,
                          mac=mac, attribute='x')

        try:
            engine.read_attribute(mac, 'x')
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.NOT_IMPLEMENTED)

    def test_write_attribute(self):
        """Test write_attribute"""

        engine = EngineBluew(name='name', version='version')
        mac = 'xx:xx:xx:xx:xx'
        self.assertRaises(EngineError,
                          engine.write_attribute,
                          mac=mac, attribute='x', data='0x00')

        try:
            engine.write_attribute(mac, 'x', '0x00')
        except EngineError as exp:
            self.assertEqual(exp.reason, EngineError.NOT_IMPLEMENTED)
