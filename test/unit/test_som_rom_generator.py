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
from nysa.cbuilder.som_rom_generator import generate_rom_image

from nysa.cbuilder.sdb import SDBInfo
from nysa.cbuilder.sdb import SDBWarning
from nysa.cbuilder.sdb import SDBError

from nysa.common.status import StatusLevel
from nysa.common.status import Status



class Test (unittest.TestCase):
    """Unit test SDB Tree"""

    def setUp(self):
        self.som = som.SOM()

    def test_generate_simple_rom(self):
        self.som.initialize_root()
        root = self.som.get_root()
        d = sdbc.create_device_record(name = "device 1", size = 0x100)
        self.som.insert_component(root, d)
        rom = generate_rom_image(self.som)
        #rom = generate_rom_image(self.som)
        #print_sdb(rom)

    def test_generate_one_sub_bus_rom(self):
        self.som.initialize_root()
        root = self.som.get_root()
        bus = self.som.insert_bus()
        d = sdbc.create_device_record(name = "device 1", size = 0x100)
        self.som.insert_component(bus, d)
        rom = generate_rom_image(self.som)
        #print_sdb(rom)
        #Need a mechanism to verify this

    def test_generate_two_sub_buses(self):
        self.som.initialize_root()
        root = self.som.get_root()
        peripheral = self.som.insert_bus()
        peripheral.set_name("peripheral")
        memory = self.som.insert_bus()
        memory.set_name("memory")
        d1 = sdbc.create_device_record(name = "device 1", size = 0x100)
        d2 = sdbc.create_device_record(name = "device 2", size = 0x100)
        m1 = sdbc.create_device_record(name = "memory 1", size = 0x10000)
        m2 = sdbc.create_device_record(name = "memory 2", size = 0x20000)
        peripheral.set_child_spacing(0x0100000000)
        self.som.insert_component(peripheral, d1)
        self.som.insert_component(peripheral, d2)
        self.som.insert_component(memory, m1)
        self.som.insert_component(memory, m2)
        rom = generate_rom_image(self.som)
        #print_sdb(rom)

    def test_generate_one_sub_bus_integration_record(self):
        self.som.initialize_root()
        root = self.som.get_root()
        bus = self.som.insert_bus()
        intr = sdbc.create_integration_record("Integration Data",
                                                vendor_id = 0x800BEAF15DEADC03,
                                                device_id = 0x00000000)
        d = sdbc.create_device_record(name = "device 1", size = 0x100)
        self.som.insert_component(bus, d)
        self.som.insert_component(bus, intr)
        rom = generate_rom_image(self.som)
        #print_sdb(rom)

    def test_generate_one_sub_bus_with_url(self):
        self.som.initialize_root()
        root = self.som.get_root()
        bus = self.som.insert_bus()
        url = sdbc.create_repo_url_record("http://www.geocities.com")
        d = sdbc.create_device_record(name = "device 1", size = 0x100)
        self.som.insert_component(bus, d)
        self.som.insert_component(root, url)
        rom = generate_rom_image(self.som)
        #print_sdb(rom)

    def test_generate_one_sub_bus_with_synthesis(self):
        self.som.initialize_root()
        root = self.som.get_root()
        bus = self.som.insert_bus()
        url = sdbc.create_repo_url_record("http://www.geocities.com")
        synthesis = sdbc.create_synthesis_record("Synthesis Name", 123, "cool tool", 1.0, "jeff")
        d = sdbc.create_device_record(name = "device 1", size = 0x100)
        self.som.insert_component(bus, d)
        self.som.insert_component(root, synthesis)
        rom = generate_rom_image(self.som)
        #print_sdb(rom)

    def test_parse_large_rom(self):
        self.som.initialize_root()
        root = self.som.get_root()
        url = sdbc.create_repo_url_record("http://www.geocities.com")
        synthesis = sdbc.create_synthesis_record("Synthesis Name", 123, "cool tool", 1.0, "jeff")
        intr = sdbc.create_integration_record("Integration Data",
                                                vendor_id = 0x800BEAF15DEADC03,
                                                device_id = 0x00000000)

        peripheral = self.som.insert_bus()
        peripheral.set_name("peripheral")
        memory = self.som.insert_bus()
        memory.set_name("memory")
        self.som.insert_component(root, url)
        self.som.insert_component(root, synthesis)
        d1 = sdbc.create_device_record(name = "device 1", size = 0x100)
        d2 = sdbc.create_device_record(name = "device 2", size = 0x100)
        m1 = sdbc.create_device_record(name = "memory 1", size = 0x10000)
        m2 = sdbc.create_device_record(name = "memory 2", size = 0x20000)
        peripheral.set_child_spacing(0x0100000000)
        self.som.insert_component(peripheral, d1)
        self.som.insert_component(peripheral, d2)
        self.som.insert_component(peripheral, intr)
        self.som.insert_component(memory, m1)
        self.som.insert_component(memory, m2)
        rom = generate_rom_image(self.som)
        #print_sdb(rom)

def print_sdb(rom):
    rom = sdbc.convert_rom_to_32bit_buffer(rom)
    rom = rom.splitlines()
    print "ROM"
    for i in range (0, len(rom), 4):
        if (i % 16 == 0):
            magic = "0x%s" % (rom[i].lower())
            last_val = int(rom[i + 15], 16) & 0xFF
            print ""
            if (magic == hex(sdbc.SDB_INTERCONNECT_MAGIC) and last_val == 0):
                print "Interconnect"
            elif last_val == 0x01:
                print "Device"
            elif last_val == 0x02:
                print "Bridge"
            elif last_val == 0x80:
                print "Integration"
            elif last_val == 0x81:
                print "URL"
            elif last_val == 0x82:
                print "Synthesis"
            elif last_val == 0xFF:
                print "Empty"
            else:
                print "???"

        print "%s %s : %s %s" % (rom[i], rom[i + 1], rom[i + 2], rom[i + 3])

