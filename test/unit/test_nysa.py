#!/usr/bin/python

import unittest
import json
import sys
import os
from array import array as Array

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.cbuilder import device_manager
from nysa.host.driver import driver

from nysa.host.platform_scanner import find_board
from nysa.host.platform_scanner import PlatformScannerException

from nysa.cbuilder.sdb_component import create_synthesis_record
from nysa.cbuilder.sdb_component import create_repo_url_record
from nysa.cbuilder.sdb_component import create_integration_record

from nysa.cbuilder.sdb import SDBError

from nysa.common.status import Status

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

    #Control Functions
    def test_set_timeout(self):
        test_val = 1000
        self.n.set_timeout(test_val)
        self.assertEqual(self.n.timeout, test_val)

    def test_get_timeout(self):
        read_val = self.n.get_timeout()
        self.assertEqual(self.n.timeout, read_val)

    def test_read(self):
        address = 0
        length = 1
        disable_auto_inc = False
        #Test Length 1 Read
        resp = self.n.read(address, length, disable_auto_inc)
        self.assertEqual(len(resp), length * 4)

        #Test Length 2 read
        address = 0
        length = 2
        disable_auto_inc = False
        resp = self.n.read(address, length, disable_auto_inc)
        self.assertEqual(len(resp), length * 4)

        #Test Read at address 0x10
        length = 1
        address = 0x10
        disable_auto_inc = False
        resp = self.n.read(address, length, disable_auto_inc)
        self.assertEqual(len(resp), length * 4)

        #Test read a memory device
        length = 1
        address = 0x00
        disable_auto_inc = False
        resp = self.n.read(address, length, disable_auto_inc)
        self.assertEqual(len(resp), length * 4)

    def test_write(self):
        address = 0
        data = Array('B', [0x00, 0x00, 0x00, 0x00])
        disable_auto_inc = False
        #Test Length 1 Read
        self.n.write(address, data, disable_auto_inc)

        #Test Length 2 read
        address = 0
        data = Array('B', [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        disable_auto_inc = False
        self.n.write(address, data, disable_auto_inc)

        #Test Read at address 0x10
        data = Array('B', [0x00, 0x00, 0x00, 0x00])
        address = 0x10
        disable_auto_inc = False
        self.n.write(address, data, disable_auto_inc)

        #Test read a memory device
        data = Array('B', [0x00, 0x00, 0x00, 0x00])
        address = 0x00
        disable_auto_inc = False
        self.n.write(address, data, disable_auto_inc)

    def test_ping(self):
        self.n.ping()

    def test_reset(self):
        self.n.reset()

    #SDB Related
    def test_get_sdb_base_address(self):
        addr = self.n.get_sdb_base_address()
        self.assertEqual(addr, 0x00)

    def test_get_number_of_devices(self):
        num_devices = self.n.get_number_of_devices()
        self.assertEqual(num_devices, 4)
        #print "num devices: %s" % str(self.n.nsm.get_all_devices_as_urns())

    def test_get_number_of_components(self):
        num_components = self.n.get_number_of_components()
        self.assertEqual(num_components, 7)
        #print "num components: %s" % str(self.n.nsm.get_all_components_as_urns())

    #Stuff to edit
    def test_get_device_address(self):
        addr = self.n.get_device_address("/top/peripheral/gpio1")
        self.assertEqual(addr, long(0x02000000))

    def test_get_device_size(self):
        size = self.n.get_device_size("/top/peripheral/gpio1")
        self.assertEqual(size, long(0x08))

    def test_is_wishbone_bus(self):
        self.assertTrue(self.n.is_wishbone_bus())

    def test_is_axie_bus(self):
        self.assertRaises(  AssertionError,
                            self.n.is_axi_bus)

    def test_get_board_name(self):
        name = self.n.get_board_name()
        self.assertEqual(name, "sim")

    def test_get_device_vendor_id(self):
        vendor_id = self.n.get_device_vendor_id("/top/peripheral/gpio1")
        self.assertEqual(vendor_id, long(0x800000000000C594))

    def test_get_device_product_id(self):
        product_id = self.n.get_device_product_id("/top/peripheral/gpio1")
        self.assertEqual(product_id, 0x00000002)

    def test_get_device_abi_class(self):
        abi_class = self.n.get_device_abi_class("/top/peripheral/gpio1")
        self.assertEqual(abi_class, 0)

    def test_get_device_abi_major(self):
        abi_major = self.n.get_device_abi_major("/top/peripheral/gpio1")
        self.assertEqual(abi_major, 2)

    def test_get_device_abi_minor(self):
        abi_minor = self.n.get_device_abi_minor("/top/peripheral/gpio1")
        self.assertEqual(abi_minor, 1)

    def test_find_device_from_name(self):
        #Test just specifying the device name
        device_name = "gpio"
        abi_minor = None
        device_list = self.n.find_device_from_name(device_name = device_name, abi_minor = abi_minor)
        self.assertIn("/top/peripheral/gpio1", device_list)
        self.assertEqual(len(device_list), 1)

        #Test specifying device name and sub type
        device_name = "gpio"
        abi_minor = 1
        device_list = self.n.find_device_from_name(device_name, abi_minor = abi_minor)
        self.assertIn("/top/peripheral/gpio1", device_list)
        self.assertEqual(len(device_list), 1)

        #Specify an incorerect type
        device_name = "hi"
        abi_minor = 1
        device_list = self.n.find_device_from_name(device_name, abi_minor = abi_minor)
        self.assertEqual(len(device_list), 0)

    def test_find_urn_from_abi(self):
        #test specify everything
        abi_class = 0
        abi_major = 2
        abi_minor = 1
        device_list = self.n.find_urn_from_abi(abi_class = abi_class, abi_major = abi_major, abi_minor = abi_minor)
        self.assertIn("/top/peripheral/gpio1", device_list)
        self.assertEqual(len(device_list), 1)

        #Test not specifying the minor
        abi_class = 0
        abi_major = 2
        abi_minor = None
        device_list = self.n.find_urn_from_abi(abi_class = abi_class, abi_major = abi_major, abi_minor = abi_minor)
        self.assertIn("/top/peripheral/gpio1", device_list)
        self.assertEqual(len(device_list), 1)

        #Test specify neither major or minor
        abi_class = 0
        abi_major = None
        abi_minor = None
        device_list = self.n.find_urn_from_abi(abi_class = abi_class, abi_major = abi_major, abi_minor = abi_minor)
        self.assertIn("/top/peripheral/gpio1", device_list)
        self.assertEqual(len(device_list), 4)

        #Test specify neither major or minor
        abi_class = None
        abi_major = None
        abi_minor = None
        device_list = self.n.find_urn_from_abi(abi_class = abi_class, abi_major = abi_major, abi_minor = abi_minor)
        self.assertIn("/top/peripheral/gpio1", device_list)
        self.assertEqual(len(device_list), 4)

        #Test specify neither major or minor
        abi_class = None
        abi_major = 5
        abi_minor = None
        device_list = self.n.find_urn_from_abi(abi_class = abi_class, abi_major = abi_major, abi_minor = abi_minor)
        self.assertEqual(len(device_list), 0)

    def test_find_urn_from_ids(self):
        urns = self.n.find_urn_from_ids(0x800000000000C594)
        self.assertEqual(len(urns), 3)
        urns = self.n.find_urn_from_ids(vendor_id = None, product_id = 0x02)
        self.assertEqual(len(urns), 1)

    def test_get_total_memory_size(self):
        size = self.n.get_total_memory_size()
        self.assertEqual(size, long(0x0800000))

    def test_is_memory_device(self):
        mem = "/top/memory/wb_sdram"
        not_mem = "/top/peripheral/gpio1"
        self.assertTrue(self.n.is_memory_device(mem))
        self.assertFalse(self.n.is_memory_device(not_mem))

    def test_is_device_in_platform(self):
        class MockGPIODriver(driver.Driver):
            def __init__(self, n, dev_id, debug):
                super(MockDriver, self).__init__(n, dev_id, debug)

            @staticmethod
            def get_abi_class():
                return 0

            @staticmethod
            def get_abi_major():
                return device_manager.get_device_id_from_name("gpio")

            @staticmethod
            def get_abi_minor():
                return None

        #print "Output: %s" % self.n.is_device_in_platform(MockGPIODriver)
        self.assertTrue(self.n.is_device_in_platform(MockGPIODriver))

    def test_find_device_using_driver(self):
        class MockGPIODriver(driver.Driver):
            def __init__(self, n, dev_id, debug):
                super(MockDriver, self).__init__(n, dev_id, debug)

            @staticmethod
            def get_abi_class():
                return 0

            @staticmethod
            def get_abi_major():
                return device_manager.get_device_id_from_name("gpio")

            @staticmethod
            def get_abi_minor():
                return None

        urns = self.n.find_device(MockGPIODriver)
        self.assertIn("/top/peripheral/gpio1", urns)

    def test_get_peripheral_device_index(self):
        urn = "/top/peripheral/gpio1"
        index = 2
        peripheral_index = self.n.get_peripheral_device_index(urn)
        self.assertEqual(index, peripheral_index)

    #Programming
    def test_upload(self):
        self.n.upload("")

    def test_program (self):
        self.n.program()

