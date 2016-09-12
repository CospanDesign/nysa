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
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return device_manager.get_device_id_from_name("gpio")

    @staticmethod
    def get_abi_minor():
        return 1

class MockDMAReaderDriver(driver.Driver):

    def __init__(self, n, urn, debug):
        super (MockDMAReaderDriver, self).__init__(n, urn, debug)
        self.dmar = driver.DMAReadController(self,
                                      mem_base0  = 0x00000000,
                                      mem_base1  = 0x00100000,
                                      size       = 0x20,
                                      reg_status = 1,
                                      reg_base0  = 0x00,
                                      reg_size0  = 0x10,
                                      reg_base1  = 0x10,
                                      reg_size1  = 0x10,
                                      timeout    = 3,
                                      finished0  = 1,
                                      finished1  = 1,
                                      empty0     = 0,
                                      empty1     = 0)


    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return device_manager.get_device_id_from_name("dma reader")

    @staticmethod
    def get_abi_minor():
        return None

class MockDMAWriterDriver(driver.Driver):

    def __init__(self, n, urn, debug):
        super (MockDMAWriterDriver, self).__init__(n, urn, debug)
        self.wdma = driver.DMAWriteController(device       = self,
                                       mem_base0    = 0x00,
                                       mem_base1    = 0x10,
                                       size         = 0x10,
                                       reg_status   = 0x00,
                                       reg_base0    = 0x01,
                                       reg_size0    = 0x02,
                                       reg_base1    = 0x03,
                                       reg_size1    = 0x04,
                                       timeout      = 3,
                                       empty0       = 0,
                                       empty1       = 1)


    @staticmethod
    def get_abi_class():
        return 0

    @staticmethod
    def get_abi_major():
        return device_manager.get_device_id_from_name("dma writer")

    @staticmethod
    def get_abi_minor():
        return None

class Test (unittest.TestCase):
    """Unit test for Nysa SDB Manager"""

    def setUp(self):
        name = "sim"
        serial = "dionysus_dma_test"
        s = Status()
        s.set_level("fatal")
        try:
            self.n = find_board(name, serial, s)
        except PlatformScannerException as ex:
            print "Could not find platform :%s" % str(ex)
            sys.exit(1)
        self.n.read_sdb()
        urns = self.n.find_device(MockGPIODriver)
        #self.simple_dev = MockGPIODriver(self.n, urns[0], True)
        self.simple_dev = MockGPIODriver(self.n, urns[0], False)
        urns = self.n.find_device(MockDMAReaderDriver)
        self.dmar = MockDMAReaderDriver(self.n, urns[0], False)

        urns = self.n.find_device(MockDMAWriterDriver)
        self.dmaw = MockDMAWriterDriver(self.n, urns[0], False)
        s.set_level("error")

    def test_write(self):
        address = 0x20
        data = Array('B', [0x00, 0x01, 0x02, 0x03])
        flags = []
        self.simple_dev.write(address, data, flags)

    def test_write_register(self):
        address = 0x030
        data = 0x00010203
        self.simple_dev.write_register(address, data)

    def test_read_register(self):
        address = 0x030
        data = self.simple_dev.read_register(address)
        self.assertEqual(data, 0)

    def test_write_memory(self):
        address = 0x00
        data = Array('B', [0x00, 0x01, 0x02, 0x03, 0x04])
        self.simple_dev.write_memory(address, data)

    def test_read(self):
        address = 0x00
        length = 10
        flags = []
        data = self.simple_dev.read(address, length, flags)
        self.assertEqual(len(data), length * 4)

    def test_read_memory(self):
        address = 0x00
        length = 10
        data = self.simple_dev.read_memory(address, length)
        self.assertEqual(len(data), length * 4)

    def test_enable_register_bit(self):
        address = 0x00
        bit = 2
        enable = True
        self.simple_dev.enable_register_bit(address, bit, enable)

    def test_set_register_bit(self):
        address = 0x00
        bit = 2
        self.simple_dev.set_register_bit(address, bit)

    def test_clear_register_bit(self):
        address = 0x00
        bit = 2
        self.simple_dev.clear_register_bit(address, bit)

    def test_is_register_bit_set(self):
        address = 0x00
        bit = 2
        self.assertFalse(self.simple_dev.is_register_bit_set(address, bit))

    def test_wait_for_interrupts(self):
        wait_time = 1
        self.simple_dev.wait_for_interrupts(wait_time)

    def test_register_dump(self):
        length = self.simple_dev.n.get_device_size(self.simple_dev.urn)
        data = self.simple_dev.register_dump()


