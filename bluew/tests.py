"""
Bluew is a python wrapper for Bluetoothctl.
Author: Ahmed Alsharif
License: MIT
"""

import unittest

from bluew import expect, Bluew


class TestExpect(unittest.TestCase):
    """
    Test cases for the CheckResponse function
    """
    good = ['Good is better than bad', ]
    bad = ['Bad is better than good', ]

    def test_expect_with_bad(self):
        """
        Test if function returns correct value when a bad value is found.
        :return:
        """
        data = ['Good is the new Bad is better than good', ]
        result = expect(good=self.good, bad=self.bad,
                        response=data)
        self.assertEqual((False, self.bad[0]), result)

    def test_expect_with_good(self):
        """
        Test if function returns correct value when a good value is found.
        :return:
        """
        data = ['Good is the new Good is better than bad', ]
        result = expect(good=self.good, bad=self.bad,
                        response=data)
        self.assertEqual((True, self.good[0]), result)

    def test_expect_neither(self):
        """
        Test if func returns False when neither good nor bad values are found.
        :return:
        """
        data = ['Good is the new Good is better than Bad', ]
        result = expect(good=self.good, bad=self.bad,
                        response=data)
        self.assertEqual(False, result)


class TestBluewNoDevice(unittest.TestCase):
    """
    Test the Bluew class. All tests here use a device
    that doesn't exist and thus don't actually test
    if these calls work when a real device is available.
    Only returns when the device is not available are
    tested here.
    """
    def test_connect(self):
        """
        Test that connect writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        mac = 'xx:xx:xx:xx:xx:xx:xx'
        res = blw.connect(mac)
        self.assertEqual(res[1], 'Device ' + mac + ' not available')

    def test_disconnect(self):
        """
        Test that disconnect writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        mac = 'xx:xx:xx:xx:xx:xx:xx'
        res = blw.disconnect(mac)
        self.assertEqual(res[1], 'Device ' + mac + ' not available')

    def test_pair(self):
        """
        Test that pair writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        mac = 'xx:xx:xx:xx:xx:xx:xx'
        res = blw.pair(mac)
        self.assertEqual(res[1], 'Device ' + mac + ' not available')

    def test_select_attribute(self):
        """
        Test that select_attribute writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        mac = 'xx:xx:xx:xx:xx:xx:xx'
        attr = 'testattr'
        res = blw.select_attribute(mac, attr)
        self.assertEqual(res[1], "Can't get device info")

    def test_write(self):
        """
        Test that write writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        res = blw.write('0x04')
        self.assertEqual(res[1], "No attribute selected")

    def test_notify(self):
        """
        Test that write writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        res = blw.notify('on')
        self.assertEqual(res[1], 'No attribute selected')

    def test_info(self):
        """
        Test that write writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        mac = 'xx:xx:zz:xx:zz:xx'
        res = blw.info(mac)
        self.assertEqual(res, {})
