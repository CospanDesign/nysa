#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))

from nysa.host.platform_scanner import find_board
from nysa.host.platform_scanner import PlatformScannerException

from nysa.cbuilder.sdb_component import create_synthesis_record
from nysa.cbuilder.sdb_component import create_repo_url_record
from nysa.cbuilder.sdb_component import create_integration_record

from nysa.cbuilder.sdb import SDBError

from nysa.common.status import Status
from common.status import StatusLevel

class Test (unittest.TestCase):
    """Unit test for Nysa SDB Manager"""

    def setUp(self):
        self.dbg = False
        name = "sim"
        serial = "dionysus_uart_pmod"
        s = Status()
        s.set_level(StatusLevel.FATAL)
        try:
            self.board = find_board(name, serial, s)
        except PlatformScannerException as ex:
            print "Could not find platform :%s" % str(ex)
            sys.exit(1)
        self.board.read_sdb()
        self.nsm = self.board.nsm

    def test_get_component_from_urn(self):
        som = self.nsm.som
        root = som.get_root()
        self.assertEqual(self.nsm._get_component_from_urn(), root)

        c = self.nsm._get_component_from_urn("/top/peripheral/gpio1")
        self.assertEqual(c.get_name(), "gpio1")

        self.assertRaises(SDBError,
                            self.nsm._get_component_from_urn,
                            "bill")

    #SOM Functions
    def test_get_all_component_as_urns(self):
        """
        Go through all the devices and return a URN that will allow users
        to obtain a unique reference to a device

        """

        som = self.nsm.som
        root = som.get_root()
        c = create_synthesis_record("test",
                                    0,
                                    "xilinx",
                                    14.1,
                                    "bill")
        som.insert_component(root, c)
        c = create_repo_url_record("http://www.example.com")
        som.insert_component(root, c)
        c = create_integration_record("integrating is fun")
        som.insert_component(root, c)

        urns = self.nsm.get_all_components_as_urns()

        #print urns
        self.assertIn("/top", urns)
        self.assertIn("/top/peripheral", urns)
        self.assertIn("/top/peripheral/SDB", urns)
        self.assertIn("/top/peripheral/uart1", urns)
        self.assertIn("/top/peripheral/gpio1", urns)
        self.assertIn("/top/memory", urns)
        self.assertIn("/top/memory/wb_sdram", urns)

    def test_get_all_devices_as_urns(self):
        urns = self.nsm.get_all_devices_as_urns()
        self.assertIn("/top/peripheral/SDB", urns)
        self.assertIn("/top/peripheral/uart1", urns)
        self.assertIn("/top/peripheral/gpio1", urns)
        self.assertIn("/top/memory/wb_sdram", urns)

        self.assertNotIn("/top", urns)
        self.assertNotIn("/top/peripheral", urns)
        self.assertNotIn("/top/memory", urns)

    def test_get_number_of_components(self):
        count = self.nsm.get_number_of_components()
        self.assertEqual(count, 7)

    def test_get_number_of_devices(self):
        count = self.nsm.get_number_of_devices()
        self.assertEqual(count, 4)

    def test_get_component_from_urn(self):
        urn = "/top/peripheral/uart1"
        c = self.nsm._get_component_from_urn(urn)
        #print "c: %s" % str(c)
        self.assertEqual(c.get_name(), "uart1")

    def test_find_device_from_ids(self):
        vendor_id = 0x800000000000C594
        product_id = 0x00000001
        urn = self.nsm.find_device_from_ids(vendor_id, product_id)
        #print "urn: %s" % urn
        self.assertEqual(urn, "/top")

    def test_find_device_from_address(self):
        address = 0x010000000
        urn = self.nsm.find_device_from_address(address)
        #print "urn: %s" % urn
        self.assertEqual(urn, "/top/peripheral/uart1")

    def test_find_device_from_abi(self):
        abi_class = 0
        abi_major = 2
        abi_minor = 1
        urn = self.nsm.find_device_from_abi(abi_class, abi_major, abi_minor)
        #print "urn: %s" % urn
        self.assertEqual(urn, "/top/peripheral/gpio1")

    def test_is_wishbone_bus(self):
        self.assertTrue(self.nsm.is_wishbone_bus())
        self.assertTrue(self.nsm.is_wishbone_bus("/top/peripheral"))
        self.assertTrue(self.nsm.is_wishbone_bus("/top/peripheral/gpio1"))

    def test_is_axi_bus(self):
        self.assertRaises(  AssertionError,
                            self.nsm.is_axi_bus)
        self.assertRaises(  AssertionError,
                            self.nsm.is_axi_bus,
                            "/top/peripheral")
        self.assertRaises(  AssertionError,
                            self.nsm.is_axi_bus,
                            "/top/peripheral/gpio1")

    def test_is_storage_bus(self):
        self.assertFalse(self.nsm.is_storage_bus())
        self.assertFalse(self.nsm.is_storage_bus("/top/peripheral"))
        self.assertFalse(self.nsm.is_storage_bus("/top/peripheral/gpio1"))

    #Device Functions
    def test_get_device_address(self):
        address = self.nsm.get_device_address("/top/peripheral/gpio1")
        som = self.nsm.som
        root = som.get_root()
        c = create_synthesis_record("test",
                                    0,
                                    "xilinx",
                                    14.1,
                                    "bill")
        som.insert_component(root, c)
        c = create_repo_url_record("http://www.example.com")
        som.insert_component(root, c)
        c = create_integration_record("integrating is fun")
        som.insert_component(root, c)

        self.assertEqual(address, long(0x020000000))

    def test_is_bus(self):
        self.assertFalse(self.nsm.is_bus("/top/peripheral/gpio1"))
        self.assertTrue(self.nsm.is_bus("/top/peripheral"))

    def test_get_device_size(self):
        size = self.nsm.get_device_size("/top/peripheral/gpio1")
        self.assertEqual(size, long(8))

    def test_get_device_vendor_id(self):
        vendor_id = self.nsm.get_device_vendor_id("/top/peripheral/gpio1")
        self.assertEqual(vendor_id, long(0x800000000000C594))

    def test_get_device_product_id(self):
        product_id = self.nsm.get_device_product_id("/top/peripheral/gpio1")
        self.assertEqual(product_id, 0x00000000)

    def test_get_device_abi_class(self):
        abi_class = self.nsm.get_device_abi_class("/top/peripheral/gpio1")
        self.assertEqual(abi_class, 0x00)

    def test_get_device_abi_major(self):
        abi_major = self.nsm.get_device_abi_major("/top/peripheral/gpio1")
        self.assertEqual(abi_major, 0x02)

    def test_get_device_abi_minor(self):
        abi_minor = self.nsm.get_device_abi_minor("/top/peripheral/gpio1")
        self.assertEqual(abi_minor, 0x01)

    def test_find_urn_from_device_type(self):
        urns = self.nsm.find_urn_from_device_type("gpio")
        self.assertEqual(len(urns), 1)
        urns = self.nsm.find_urn_from_device_type("experiment")
        self.assertEqual(len(urns), 0)

    def test_find_urn_from_ids(self):
        urns = self.nsm.find_urn_from_ids(0x800000000000C594)
        self.assertEqual(len(urns), 3)
        urns = self.nsm.find_urn_from_ids(vendor_id = None, product_id = 0x00)
        self.assertEqual(len(urns), 4)
        #print "urns: %s" % str(urns)

    def test_get_total_memory_size(self):
        size = self.nsm.get_total_memory_size()
        #print "size: 0x%016X" % size
        self.assertEqual(size, long(0x0800000))


