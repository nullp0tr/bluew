"""
Bluew is a python wrapper for Bluetoothctl.
Author: Ahmed Alsharif
License: MIT
"""

import unittest

from bluew import *


class TestCheckResponse(unittest.TestCase):
    good = ['Good is better than bad', ]
    bad = ['Bad is better than good', ]

    def test_check_response_with_bad(self):
        data = ['Good is the new Bad is better than good', ]
        result = Bluew._check_response(Bluew(), good=self.good, bad=self.bad,
                                       response=data)
        self.assertEqual((False, self.bad[0]), result)

    def test_check_response_with_good(self):
        data = ['Good is the new Good is better than bad', ]
        result = Bluew._check_response(Bluew(), good=self.good, bad=self.bad,
                                       response=data)
        self.assertEqual((True, self.good[0]), result)

    def test_check_response_with_neither(self):
        data = ['Good is the new Good is better than Bad', ]
        result = Bluew._check_response(Bluew(), good=self.good, bad=self.bad,
                                       response=data)
        self.assertEqual(False, result)
