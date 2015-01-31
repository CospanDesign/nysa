#!/usr/bin/python

import unittest
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from nysa.cbuilder import sdb_component as sdbc
from nysa.cbuilder import sdb_object_model as som

from nysa.cbuilder.sdb import SDBInfo
from nysa.cbuilder.sdb import SDBWarning
from nysa.cbuilder.sdb import SDBError

from nysa.common.status import StatusLevel
from nysa.common.status import Status

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
    """Unit test SDB Tree"""

    def setUp(self):
        self.status = Status()
        self.status.set_level(StatusLevel.VERBOSE)
        self.som = som.SOM()

    def test_initialize_root(self):
        self.som.initialize_root()

    def test_initialize_root_with_good_params(self):
        self.som.initialize_root(
                          name = "test",
                          version = 1,
                          vendor_id = 0x800BEAF15DEADC03,
                          entity_id = 0x00000001,
                          bus_type = "wishbone")

    def test_initialize_root_with_version_error(self):
        self.assertRaises(SDBError,
                            self.som.initialize_root,
                            name = "test",
                            version = 2,
                            vendor_id = 0x800BEAF15DEADC03,
                            entity_id = 0x00000001,
                            bus_type = "wishbone")

    def test_initialize_root_with_bad_bus(self):
        self.assertRaises(SDBError,
                          self.som.initialize_root,
                          name = "test",
                          version = 1,
                          vendor_id = 0x800BEAF15DEADC03,
                          entity_id = 0x00000001,
                          bus_type = "bad bus")

    def test_insert_bus(self):
        self.som.initialize_root()
        self.som.insert_bus()
        self.assertTrue(self.som.is_entity_a_bus(root = None, index = 0))

    def test_insert_entity(self):
        self.som.initialize_root()
        c = sdbc.SDBComponent()
        c.parse_buffer(SDB_DATA)
        c.set_size(5)
        c.d["SDB_RECORD_TYPE"] = sdbc.SDB_RECORD_TYPE_DEVICE
        self.som.insert_component(component = c)
        self.assertFalse(self.som.is_entity_a_bus(root = None, index = 0))

    def test_get_child_count(self):
        self.som.initialize_root()
        c = sdbc.SDBComponent()
        c.parse_buffer(SDB_DATA)
        c.set_size(5)
        c.d["SDB_RECORD_TYPE"] = sdbc.SDB_RECORD_TYPE_DEVICE
        self.som.insert_component(component = c)
        self.assertEqual(self.som.get_child_count(), 1)

    def test_get_component(self):
        self.som.initialize_root()
        c = sdbc.SDBComponent()
        c.parse_buffer(SDB_DATA)
        c.set_size(5)
        c.d["SDB_RECORD_TYPE"] = sdbc.SDB_RECORD_TYPE_DEVICE
        self.som.insert_component(component = c)
        self.assertEqual(self.som.get_component(index = 0), c)

    def test_set_bus_name_for_root(self):
        self.som.initialize_root()
        root = self.som.get_root()
        self.som.set_bus_name(root, "Top")
        self.assertEqual(root.c.d["SDB_NAME"], "Top")

    def test_set_bus_name_for_not_root(self):
        self.som.initialize_root()
        root = self.som.get_root()
        self.som.insert_bus()
        bus = self.som.get_buses()[0]
        self.som.set_bus_name(bus, "peripherals")
        self.assertEqual(bus.c.d["SDB_NAME"], "peripherals")

    def test_set_spacing(self):
        self.som.initialize_root()
        root = self.som.get_root()
        spacing = 0x100
        root.set_child_spacing(spacing)
        bus = self.som.insert_bus()
        dev = sdbc.create_device_record(name = "test 1",
                                        size = 0x10)
        self.som.insert_component(bus, dev)

        self.som.insert_bus()

        #print "Number of components: %d" % self.som.get_child_count(root)
        bus = self.som.get_buses()[1]

        #self.som.set_bus_start_address(bus, start_address)
        #print "bus start address: 0x%08X" % bus.c.get_start_address_as_int()
        self.assertEqual(bus.c.get_start_address_as_int(), spacing)

    def test_remove_bus_root(self):
        self.som.initialize_root()
        root = self.som.get_root()
        self.assertRaises(SDBError,
                          self.som.remove_bus,
                          root)

    def test_remove_bus_bad_parent(self):
        self.som.initialize_root()
        class A (object):
            def get_parent(self):
                return None
        a = A()
        self.assertRaises(SDBError,
                          self.som.remove_bus,
                          a)

    def test_remove_bus(self):
        self.som.initialize_root()
        root = self.som.get_root()
        self.som.insert_bus()
        self.som.insert_bus()
        self.assertEqual(self.som.get_child_count(root), 2)
        self.som.remove_bus(self.som.get_buses()[0])
        self.assertEqual(self.som.get_child_count(root), 1)

    def test_insert_component_with_interconnect_fail(self):
        self.som.initialize_root()
        root = self.som.get_root()
        int_record = sdbc.create_interconnect_record()
        self.assertRaises(  SDBError,
                            self.som.insert_component,
                            root,
                            int_record)

    def test_insert_component(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din = sdbc.create_device_record()
        self.som.insert_component(root, din)
        dout = self.som.get_component(root, 0)
        self.assertEqual(din, dout)

    def test_update_method_at_root(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "Test 1", size = 0x10)
        din2 = sdbc.create_device_record(name = "Test 2", size = 0x20)
        self.som.insert_component(root, din1)
        self.som.insert_component(root, din2)
        dout = self.som.get_component(root, 0)
        self.assertEqual(din1, dout)

        dout = self.som.get_component(root, 1)
        self.assertEqual(dout.get_start_address_as_int(), 0x10)

    def test_update_method_at_subbus(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "Test 1", size = 0x10)
        din2 = sdbc.create_device_record(name = "Test 2", size = 0x20)

        bus = self.som.insert_bus()

        self.som.insert_component(root = bus, component = din1)
        self.som.insert_component(root = bus, component = din2)

        dout = self.som.get_component(bus, 0)
        self.assertEqual(din1, dout)

        dout = self.som.get_component(bus, 1)
        self.assertEqual(dout.get_start_address_as_int(), 0x10)

    def test_update_method_after_remove(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "Test 1", size = 0x10)
        din2 = sdbc.create_device_record(name = "Test 2", size = 0x20)
        din3 = sdbc.create_device_record(name = "Test 3", size = 0x30)

        bus = self.som.insert_bus()

        self.som.insert_component(root = bus, component = din1)
        self.som.insert_component(root = bus, component = din2)
        self.som.insert_component(root = bus, component = din3)

        self.som.remove_component_by_index(bus, 0)

        dout = self.som.get_component(bus, 0)
        self.assertEqual(din2, dout)

        dout = self.som.get_component(bus, 1)
        self.assertEqual(dout.get_start_address_as_int(), 0x20)

    def test_set_bus_name(self):
        test_name = "Renamed Bus"
        self.som.initialize_root()
        root = self.som.get_root()
        bus = self.som.insert_bus()
        self.som.set_bus_name(bus, test_name)
        name = self.som.get_bus_name(bus)
        self.assertEqual(test_name, name)

    def test_insert_component(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t", size = 0x10)
        self.som.insert_component(root = root, component = din1)

        comp = self.som.get_component(root, 0)
        self.assertEqual(din1, comp)

    def test_get_component_bad_index(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t", size = 0x10)
        self.som.insert_component(root = root, component = din1)

        self.assertRaises(  IndexError,
                            self.som.get_component,
                            root,
                            1)

    def test_remove_component(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t", size = 0x10)
        self.som.insert_component(root = root, component = din1)

        self.som.remove_component_by_index(root, 0)
        count = self.som.get_child_count(root)
        self.assertEqual(count, 0)

    def test_remove_component_bad_index(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t", size = 0x10)
        self.som.insert_component(root = root, component = din1)

        self.assertRaises(  IndexError,
                            self.som.remove_component_by_index,
                            root,
                            3)

    def test_insert_integration_record(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t0", size = 0x10)
        din2 = sdbc.create_device_record(name = "t1", size = 0x10)
        din3 = sdbc.create_device_record(name = "t3", size = 0x10)

        self.som.insert_component(root, din1)
        self.som.insert_component(root, din2)
        self.som.insert_component(root, din3)
        irec = sdbc.create_integration_record( "integration test",
                                                vendor_id = 0x00,
                                                device_id = 0x00)

        self.som.insert_component(root, irec, 0)
        record = self.som.get_component(root, 3)
        self.assertEqual(record, irec)

    def test_insert_url(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t0", size = 0x10)
        din2 = sdbc.create_device_record(name = "t1", size = 0x10)
        din3 = sdbc.create_device_record(name = "t3", size = 0x10)

        self.som.insert_component(root, din1)
        self.som.insert_component(root, din2)
        self.som.insert_component(root, din3)

        url = sdbc.create_repo_url_record(   "http://www.geocities.com")
        self.som.insert_component(root, url, 1)
        record = self.som.get_component(root, 3)
        self.assertEqual(record, url)

    def test_insert_synthesis_record(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t0", size = 0x10)
        din2 = sdbc.create_device_record(name = "t1", size = 0x10)
        din3 = sdbc.create_device_record(name = "t3", size = 0x10)

        self.som.insert_component(root, din1)
        self.som.insert_component(root, din2)
        self.som.insert_component(root, din3)

        synthesis = sdbc.create_synthesis_record(   synthesis_name = "image.bit",
                                                    commit_id = 01234567,
                                                    tool_name = "xilinx xst",
                                                    tool_version = 14.1,
                                                    user_name = "dave.mccoy@cospandesign.com")
        self.som.insert_component(root, synthesis, 1)
        record = self.som.get_component(root, 3)
        self.assertEqual(record, synthesis)

    def test_move_device(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "t0", size = 0x10)
        din2 = sdbc.create_device_record(name = "t1", size = 0x10)
        din3 = sdbc.create_device_record(name = "t3", size = 0x10)

        self.som.insert_component(root, din1)
        self.som.insert_component(root, din2)
        self.som.insert_component(root, din3)

        self.som.move_component(root, 2, root, 0)
        component = self.som.get_component(root, 0)
        self.assertEqual(din3, component)

    def test_iterate_bus(self):
        self.som.initialize_root()
        root = self.som.get_root()
        din1 = sdbc.create_device_record(name = "Sub Item 1", size = 0x10)
        din2 = sdbc.create_device_record(name = "Sub Item 2", size = 0x20)

        bus = self.som.insert_bus()
        bus.set_name("test bus")

        self.som.insert_component(root = bus, component = din1)
        self.som.insert_component(root = bus, component = din2)

        dout = self.som.get_component(bus, 0)
        self.assertEqual(din1, dout)
        #print "in bus: %s" % bus.get_name()
        #for entity in bus:
        #    print "\t%s" % entity.get_name()
        count = 0
        for entity in bus:
            count += 1

        self.assertEqual(count, 2)
            




