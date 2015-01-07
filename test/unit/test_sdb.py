#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from nysa.cbuilder import sdb

SDB_DATA =  \
    "  Set the Vendor ID (Hexidecimal 64-bit Number)\n" \
    "  SDB_VENDOR_ID:800000000000C594\n" \
    "\n" \
    "  Set the Product ID\n" \
    "  SDB_DEVICE_ID:0001\n" \
    "\n" \
    "  Set the Version of the core\n" \
    "  SDB_CORE_VERSION:00.000.001\n" \
    "\n" \
    "  Set the name of the core\n" \
    "  SDB_NAME:sdb_module\n" \
    "\n" \
    "  Set ABI Class\n" \
    "  SDB_ABI_CLASS:0000\n" \
    "    Undocumented Device\n" \
    "\n" \
    "  Set API Version Major\n" \
    "  SDB_ABI_VERSION_MAJOR:01\n" \
    "\n" \
    "  Set ABI Version Minor\n" \
    "  SDB_ABI_VERSION_MINOR:00\n" \
    "\n" \
    "  Set Endian BIG, LITTLE\n" \
    "  SDB_ABI_ENDIAN:BIG\n" \
    "\n" \
    "  Set Device Width (8, 16, 32, 64)\n" \
    "  SDB_ABI_DEVICE_WIDTH:32\n" \
    "\n" \
    "  Set the Modules URL\n" \
    "  SDB_MODULE_URL:http://www.example.com\n" \
    "\n" \
    "  Date\n" \
    "  SDB_DATE:2015/01/05\n" \
    "\n" \
    "  Device is executable\n" \
    "  SDB_EXECUTABLE:True\n" \
    "\n" \
    "  Device is writeable\n" \
    "  SDB_WRITEABLE:True\n" \
    "\n" \
    "  Device is readable\n" \
    "  SDB_READABLE:True\n" \
    "\n"


class Test (unittest.TestCase):
    """Unit test for arbiter"""

    def setUp(self):
        self.dbg = False
        self.sdb = sdb.SDB()
        self.sdb.parse_buffer(SDB_DATA)
        self.sdb.set_start_address(0x01000000)
        self.sdb.set_size(5)
        self.sdb.set_number_of_records(10)
        self.sdb.set_bridge_child_addr(0x1000000000000000)

    def test_parse_buffer(self):

        od = self.sdb.generated_ordered_dict()
        self.assertEqual(od["SDB_VENDOR_ID"]         , "800000000000C594")
        self.assertEqual(od["SDB_DEVICE_ID"]         , "0001")
        self.assertEqual(od["SDB_CORE_VERSION"]      , "00.000.001")
        self.assertEqual(od["SDB_NAME"]              , "sdb_module")
        self.assertEqual(od["SDB_ABI_CLASS"]         , "0000")
        self.assertEqual(od["SDB_ABI_VERSION_MAJOR"] , "01")
        self.assertEqual(od["SDB_ABI_VERSION_MINOR"] , "00")
        self.assertEqual(od["SDB_ABI_ENDIAN"]        , "BIG")
        self.assertEqual(od["SDB_ABI_DEVICE_WIDTH"]  , "32")
        self.assertEqual(od["SDB_MODULE_URL"]        , "http://www.example.com")
        self.assertEqual(od["SDB_DATE"]              , "2015/01/05")
        self.assertEqual(od["SDB_EXECUTABLE"]        , "True")
        self.assertEqual(od["SDB_WRITEABLE"]         , "True")
        self.assertEqual(od["SDB_READABLE"]          , "True")
        self.assertEqual(od["SDB_START_ADDRESS"]     , "0x1000000")
        self.assertEqual(od["SDB_LAST_ADDRESS"]      , "0x1000005")
        self.assertEqual(od["SDB_NRECS"]             , "10")
        self.assertEqual(od["SDB_BRIDGE_CHILD_ADDR"] , "0x1000000000000000")

        for e in od:
            print "%s:%s" % (e, od[e])

    def test_generate_interconnect_rom_buffer(self):
        rom = self.sdb.generate_interconnect_rom()
        buf = sdb.convert_rom_to_32bit_buffer(rom)
        print "Interconnect ROM Buffer"
        print buf
        self.assertEqual(buf, "5344422D\n" \
                              "00100100\n" \
                              "00000000\n" \
                              "01000000\n" \
                              "00000000\n" \
                              "01000005\n" \
                              "80000000\n" \
                              "0000C594\n" \
                              "00000001\n" \
                              "00000001\n" \
                              "140F0105\n" \
                              "7364625F\n" \
                              "6D6F6475\n" \
                              "6C650000\n" \
                              "00000000\n" \
                              "00000001\n")

    def test_generate_bridge_rom_buffer(self):
        rom = self.sdb.generate_bridge_rom()
        buf = sdb.convert_rom_to_32bit_buffer(rom)
        print "Bridge ROM Buffer"
        print buf

        self.assertEqual(buf, "10000000\n" \
                              "00000000\n" \
                              "00000000\n" \
                              "01000000\n" \
                              "00000000\n" \
                              "01000005\n" \
                              "80000000\n" \
                              "0000C594\n" \
                              "00000001\n" \
                              "00000001\n" \
                              "140F0105\n" \
                              "7364625F\n" \
                              "6D6F6475\n" \
                              "6C650000\n" \
                              "00000000\n" \
                              "00000001\n")

    def test_generate_device_rom_buffer(self):
        rom = self.sdb.generate_device_rom()
        buf = sdb.convert_rom_to_32bit_buffer(rom)
        print "Device ROM Buffer"
        print buf
        self.assertEqual(buf,"00000100\n" \
                             "00000207\n" \
                             "00000000\n" \
                             "01000000\n" \
                             "00000000\n" \
                             "01000005\n" \
                             "80000000\n" \
                             "0000C594\n" \
                             "00000001\n" \
                             "00000001\n" \
                             "140F0105\n" \
                             "7364625F\n" \
                             "6D6F6475\n" \
                             "6C650000\n" \
                             "00000000\n" \
                             "00000001\n")

