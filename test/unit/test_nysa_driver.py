#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.platform_scanner import find_board
from nysa.host.platform_scanner import PlatformScannerException
from nysa.host.driver import driver

from nysa.common.status import Status

from nysa.cbuilder import device_manager

class MockGPIODriver(driver.Driver):

    @staticmethod
    def get_abi_major():
        return device_manager.get_device_id_from_name("gpio")

    @staticmethod
    def get_abi_minor():
        return 1

class Test (unittest.TestCase):
    """Unit test for Nysa SDB Manager"""

    def setUp(self):
        name = "sim"
        serial = "dionysus_uart_pmod"
        s = Status()
        s.set_level("fatal")
        try:
            self.n = find_board(name, serial, s)
        except PlatformScannerException as ex:
            print "Could not find platform :%s" % str(ex)
            sys.exit(1)
        self.n.read_sdb()

    def test_dunno(self):
        pass
