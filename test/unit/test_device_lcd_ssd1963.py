#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.driver import lcd_SSD1963
from nysa.common.status import Status

class Test (unittest.TestCase):

    def setUp(self):
        s = Status()
        s.set_level("fatal")

        print "Unit test!"
        pass
        '''
        for name in get_platforms():
            try:
                self.n = find_board(name, status = s)
            except PlatformScannerException as ex:
                pass
        self.n.read_sdb()
        urns = self.n.find_device(I2C)
        self.simple_dev = MockGPIODriver(self.n, urns[0], False)
        s.set_level("error")
        '''

    def notest_lcd_SSD1963(self):
        pass
