"""
Bluew is a python wrapper for Bluetoothctl.
Author: Ahmed Alsharif
License: MIT
"""

import io
import unittest
from queue import Queue
from nose.plugins.attrib import attr
from testconfig import config

from bluew import expect, Bluew, enq_o, BluewNotifier, \
    BluewNotifierError, strip_read, strip_info


class TestExpect(unittest.TestCase):
    """
    Test cases for the expect function
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


class TestEnqueue(unittest.TestCase):
    """
    Test cases for enq_q function
    """

    def test_enq_o(self):
        """
        test that enq_o does puts line in queue
        :return: Assertion
        """
        output_text = 'Are you a triangle?'
        out = io.StringIO(output_text)
        queue = Queue()
        enq_o(out, queue, eof='')
        self.assertEqual(queue.queue[0], output_text)


class TestStripRead(unittest.TestCase):
    """
    Test cases for strip_read()
    """

    def test_no_attributes(self):
        """
        Test that strip_read() returns empty list
        when no attributes are found.
        :return: Assertion
        """
        output_data = ["Naaah" for _ in range(10)]
        result = strip_read(output_data)
        self.assertEqual(result, [])

    def test_with_attributes(self):
        """
        Test that strip_read() returns values list
        when attributes are found.
        :return: Assertion
        """
        values = ['0x04' for _ in range(10)]
        output_data = ['Attribute band Value: 0x04\n' for _ in range(10)]
        result = strip_read(output_data)
        self.assertEqual(result, values)


class TestStripInfo(unittest.TestCase):
    """
    Test cases for strip_info()
    """
    blctl_output_data = [
        '\x1b[0;94m[Raquena Myoband]\x1b[0m# info F9:3E:74:7D:3C:45\n',
        'Device F9:3E:74:7D:3C:45\n', '\tName: Raquena Myoband\n',
        '\tAlias: Raquena Myoband\n', '\tAppearance: 0x03c0\n',
        '\tPaired: no\n', '\tTrusted: no\n', '\tBlocked: no\n',
        '\tConnected: yes\n', '\tLegacyPairing: no\n',
        '\tUUID: Generic Access Profile    '
        '(00001800-0000-1000-8000-00805f9b34fb)\n',
        '\tUUID: Generic Attribute Profile '
        '(00001801-0000-1000-8000-00805f9b34fb)\n',
        '\tUUID: Device Information        '
        '(0000180a-0000-1000-8000-00805f9b34fb)\n',
        '\tUUID: Battery Service           '
        '(0000180f-0000-1000-8000-00805f9b34fb)\n',
        '\tUUID: Vendor specific           '
        '(d5060001-a904-deb9-4748-2c7f4a124842)\n',
        '\tUUID: Vendor specific           '
        '(d5060002-a904-deb9-4748-2c7f4a124842)\n',
        '\tUUID: Vendor specific           '
        '(d5060003-a904-deb9-4748-2c7f4a124842)\n',
        '\tUUID: Vendor specific           '
        '(d5060004-a904-deb9-4748-2c7f4a124842)\n',
        '\tUUID: Vendor specific           '
        '(d5060005-a904-deb9-4748-2c7f4a124842)\n',
        '\tUUID: Vendor specific           '
        '(d5060006-a904-deb9-4748-2c7f4a124842)\n',
        '\x1b[0;94m[Raquena Myoband]\x1b[0m# \n', '\x1b[K\n']

    stripped_info = {'LegacyPairing': 'no',
                     'Device': 'F9:3E:74:7D:3C:45',
                     'Trusted': 'no',
                     'Connected': 'yes',
                     'Paired': 'no',
                     'Name': 'Raquena Myoband',
                     'Alias': 'Raquena Myoband',
                     'Blocked': 'no'}

    def test_with_info(self):
        """
        Test that strip_info returns correct dict.
        :return: Assertion
        """
        result = strip_info(TestStripInfo.blctl_output_data)
        self.assertEqual(result, TestStripInfo.stripped_info)

    def test_without_info(self):
        """
        Test that strip_info returns empty dict.
        :return: Assertion
        """
        blctl_output_data = ['sdtrfidjfsdfsdfe',
                             'lkjsdijglksjielk',
                             'ksjldijglkeiququ',
                             'jsjsuejdugjfdkjg']
        result = strip_info(blctl_output_data)
        self.assertEqual(result, {})
        return


@attr('require_dev')
class TestBluewWithDevice(unittest.TestCase):
    """
    Test the Bluew class with the mac address,
    set in .testconfig.yaml. Don't run these
    tests if you don't have a bl device available.
    """

    try:
        mac = config['devices']['testdev1']['mac_address']
        false_attribute = config['devices']['testdev1']['false_attribute']
        correct_attribute = config['devices']['testdev1']['correct_attribute']
    except KeyError:
        pass

    def test_connect(self):
        """
        Test that connect() connects to dev.
        :return: Assertion.
        """
        blw = Bluew()
        mac = self.mac
        res = blw.connect(mac)
        self.assertEqual(res[0], True)
        res = blw.connect(mac)
        self.assertEqual(res[1], 'Already connected')

    def test_disconnect(self):
        """
        Test that disconnect() disconnects from dev.
        :return: Assertion.
        """
        blw = Bluew()
        mac = self.mac
        res = blw.disconnect(mac)
        self.assertEqual(res[0], True)
        res = blw.disconnect(mac)
        self.assertEqual(res[0], True)
        res = blw.disconnect(mac)
        self.assertEqual(res[1], 'Already disconnected')

    def test_pair(self):
        """
        Test that pair() pairs with dev.
        :return: Assertion
        """
        blw = Bluew()
        mac = self.mac
        res = blw.pair(mac)
        self.assertEqual(res[0], True)

    def test_select_attribute(self):
        """
        Test that select-attribute() selects attribute.
        :return: Assertion
        """
        blw = Bluew()
        mac = self.mac
        blw.connect(mac)
        bl_attr = self.false_attribute
        res = blw.select_attribute(mac, bl_attr)
        self.assertEqual(res[0], False)
        bl_attr = self.correct_attribute
        res = blw.select_attribute(mac, bl_attr)
        self.assertEqual(res[0], True)
        blw.disconnect(mac)

    def test_write(self):
        """
        Test that write() attempts to write.
        :return: Assertion
        """
        blw = Bluew()
        blw.connect(self.mac)
        blw.select_attribute(self.mac, self.correct_attribute)
        res = blw.write('0x00')
        self.assertEqual(res[0], True)
        blw.disconnect(self.mac)

    def test_read(self):
        """
        Test that read() reads from attribute
        :return: Assertion
        """
        blw = Bluew()
        res = blw.connect(self.mac)
        self.assertEqual(res[0], True)
        res = blw.select_attribute(self.mac, self.correct_attribute)
        self.assertEqual(res[0], True)
        res = blw.read()
        read_data = ['0x00', '0x00', '0x00',
                     '0x00', '0x00', '0x00',
                     '0x00', '0x00', '0x00',
                     '0x00', '0x00', '0x00',
                     '0x00', '0x00', '0x00',
                     '0x00', '0x00', '0x00',
                     '0x00', '0x00']
        self.assertEqual(res, read_data)
        blw.disconnect(self.mac)

    def test_swrite(self):
        """
        Test that swrite() writes to attribute.
        :return: Assertion
        """
        blw = Bluew()
        res = blw.connect(self.mac)
        self.assertEqual(res[0], True)
        res = blw.select_attribute(self.mac, self.correct_attribute)
        self.assertEqual(res[0], True)
        res = blw.swrite('0x01')
        self.assertEqual(res[0], True)


class TestBluewNoDevice(unittest.TestCase):
    """
    Test the Bluew class. All tests here use a device
    that doesn't exist and thus don't actually test
    if these calls work when a real device is available.
    Only returns when the device is not available are
    tested here.
    """

    def test_blctl_bin(self):
        """
        Test if bleuw throws exceptions when blctl binary
        is not found.
        :return: Assertion
        """
        self.assertRaises(FileNotFoundError, Bluew, blctl_bin='blblblblblbl')

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
        bl_attr = 'testattr'
        res = blw.select_attribute(mac, bl_attr)
        self.assertEqual(res[1], "Can't get device info")

    def test_write(self):
        """
        Test that write() writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        res = blw.write('0x04')
        self.assertEqual(res[1], "No attribute selected")

    def test_read(self):
        """
        Test that read() writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        res = blw.read()
        self.assertEqual(res, [])

    def test_swrite(self):
        """
        Test that swrite() writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        res = blw.swrite('0x04')
        self.assertEqual(res[1], "No attribute selected")
        res = blw.swrite('10', base16=False)
        self.assertEqual(res[1], "No attribute selected")

    def test_swrite_base(self):
        """
        Test that swrite() checks base.
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        self.assertRaises(ValueError, blw.swrite, data='10')

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

    def test_scan(self):
        """
        Test that write writes to the bluetoothctl
        :return: Assertion
        """
        try:
            blw = Bluew(clean_q=True)
        except FileNotFoundError:
            return
        res = blw.scan('on')
        self.assertEqual(res[1], 'Discovery started')
        res = blw.scan('on')
        self.assertEqual(res[1], 'Failed to start discovery')
        res = blw.scan('off')
        self.assertEqual(res[1], 'Discovery stopped')
        res = blw.scan('off')
        self.assertEqual(res[1], 'Failed to stop discovery')

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


class TestBluewNotifier(unittest.TestCase):
    """
    Test BluewNotifier
    """

    def test_connect_fail(self):
        """
        Test that BluewNotifier raises BlueNotifierError
        when wrong mac is used.
        :return: Assertion
        """
        try:
            self.assertRaises(BluewNotifierError,
                              BluewNotifier,
                              mac='xx:xx:xx:xx:xx',
                              attribute='llllllll')
        except FileNotFoundError:
            # bluetoothctl not available on travis
            return
        try:
            BluewNotifier(mac='xx:xx:xx:xx:xx', attribute='llllllll')
        except BluewNotifierError as blw_notif_exception:
            self.assertEqual(blw_notif_exception.step, "connecting")

    def test_select_fail(self):
        """
                Test that BluewNotifier raises BlueNotifierError
                when wrong mac is used.
                :return: Assertion
                """
        try:
            self.assertRaises(BluewNotifierError,
                              BluewNotifier,
                              mac='xx:xx:xx:xx:xx',
                              attribute='llllllll',
                              no_connect=True)
        except FileNotFoundError:
            return
        try:
            BluewNotifier(mac='xx:xx:xx:xx:xx',
                          attribute='llllllll',
                          no_connect=True)
        except BluewNotifierError as blw_notif_exception:
            self.assertEqual(blw_notif_exception.step, "selecting attribute")

    def test_notify_fail(self):
        """
                Test that BluewNotifier raises BlueNotifierError
                when wrong mac is used.
                :return: Assertion
                """
        try:
            self.assertRaises(BluewNotifierError,
                              BluewNotifier,
                              mac='xx:xx:xx:xx:xx',
                              attribute='llllllll',
                              no_connect=True,
                              no_select=True)
        except FileNotFoundError:
            return
        try:
            BluewNotifier(mac='xx:xx:xx:xx:xx',
                          attribute='llllllll',
                          no_connect=True,
                          no_select=True)
        except BluewNotifierError as blw_notif_exception:
            self.assertEqual(blw_notif_exception.step, "setting notify")

    def test_without_c_s_n(self):
        """
        Test that BluewNotifier raises BlueNotifierError
        when wrong mac is used.
        :return: Assertion
        """
        try:
            blwn = BluewNotifier(mac='xx:xx:xx:xx:xx',
                                 attribute='llllllll',
                                 no_connect=True,
                                 no_select=True,
                                 no_notify=True)
        except FileNotFoundError:
            return
        self.assertEqual(blwn.ready, True)
        self.assertEqual(blwn.data, [])
