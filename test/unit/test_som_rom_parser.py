#!/usr/bin/python

import unittest
import json
import sys
import os
import string

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.pardir,
                             os.pardir))


from nysa.cbuilder import sdb_component as sdbc
from nysa.cbuilder import sdb_object_model as som
from nysa.cbuilder.som_rom_parser import parse_rom_image
from nysa.cbuilder.som_rom_generator import generate_rom_image

from nysa.cbuilder.sdb import SDBInfo
from nysa.cbuilder.sdb import SDBWarning
from nysa.cbuilder.sdb import SDBError

from nysa.common.status import StatusLevel
from nysa.common.status import Status



class Test (unittest.TestCase):
    """Unit test SDB Tree"""

    def setUp(self):
        pass

    '''
    def test_simple_rom(self):
        rom_in = ROM1
        som = parse_rom_image(rom_in)
        rom_out = generate_rom_image(som)
        rom_out = sdbc.convert_rom_to_32bit_buffer(rom_out)
        self.assertEqual(rom_in, rom_out)
    '''

    def test_full_bus(self):
        sm = som.SOM()
        sm.initialize_root()
        root = sm.get_root()
        peripheral = sm.insert_bus()
        peripheral.set_name("peripheral")
        memory = sm.insert_bus()
        memory.set_name("memory")
        d1 = sdbc.create_device_record(name = "device 1", size = 0x100)
        d2 = sdbc.create_device_record(name = "device 2", size = 0x100)
        m1 = sdbc.create_device_record(name = "memory 1", size = 0x10000)
        m2 = sdbc.create_device_record(name = "memory 2", size = 0x20000)
        peripheral.set_child_spacing(0x0010000000)
        root.set_child_spacing      (0x0100000000)
        sm.insert_component(peripheral, d1)
        sm.insert_component(peripheral, d2)
        sm.insert_component(memory, m1)
        sm.insert_component(memory, m2)
        rom = generate_rom_image(sm)
        rom_in = sdbc.convert_rom_to_32bit_buffer(rom)
 
        #rom_in = ROM2
        #print_sdb_rom(rom_in)
        sm = parse_rom_image(rom_in)
        rom_out = generate_rom_image(sm)
        rom_out = sdbc.convert_rom_to_32bit_buffer(rom_out)
        #print_sdb_rom(rom_out)
        self.assertEqual(rom_in, rom_out)

    def test_full_bus_with_integration(self):
        sm = som.SOM()
        sm.initialize_root()
        root = sm.get_root()
        peripheral = sm.insert_bus()
        peripheral.set_name("peripheral")
        memory = sm.insert_bus()
        memory.set_name("memory")
        d1 = sdbc.create_device_record(name = "device 1", size = 0x100)
        d2 = sdbc.create_device_record(name = "device 2", size = 0x100)
        m1 = sdbc.create_device_record(name = "memory 1", size = 0x10000)
        m2 = sdbc.create_device_record(name = "memory 2", size = 0x20000)
        intr = sdbc.create_integration_record("Integration Data",
                                                vendor_id = 0x800BEAF15DEADC03,
                                                device_id = 0x00000000)

        peripheral.set_child_spacing(0x0100000000)
        sm.insert_component(peripheral, intr)
        sm.insert_component(peripheral, d1)
        sm.insert_component(peripheral, d2)
        sm.insert_component(memory, m1)
        sm.insert_component(memory, m2)
        rom = generate_rom_image(sm)
        rom_in = sdbc.convert_rom_to_32bit_buffer(rom)
 
        #rom_in = ROM2
        #print_sdb_rom(rom_in)
        sm = parse_rom_image(rom_in)
        rom_out = generate_rom_image(sm)
        rom_out = sdbc.convert_rom_to_32bit_buffer(rom_out)
        #print_sdb_rom(rom_out)
        #compare_roms(rom_in, rom_out)
        self.assertEqual(rom_in, rom_out)

    def test_generate_one_sub_bus_with_url(self):
        sm = som.SOM()
        sm.initialize_root()
        root = sm.get_root()
        peripheral = sm.insert_bus()
        peripheral.set_name("peripheral")
        memory = sm.insert_bus()
        memory.set_name("memory")
        d1 = sdbc.create_device_record(name = "device 1", size = 0x100)
        d2 = sdbc.create_device_record(name = "device 2", size = 0x100)
        m1 = sdbc.create_device_record(name = "memory 1", size = 0x10000)
        m2 = sdbc.create_device_record(name = "memory 2", size = 0x20000)
        intr = sdbc.create_integration_record("Integration Data",
                                                vendor_id = 0x800BEAF15DEADC03,
                                                device_id = 0x00000000)
        url = sdbc.create_repo_url_record("http://www.geocities.com")
        sm.insert_component(root, url)

        peripheral.set_child_spacing(0x0100000000)
        sm.insert_component(peripheral, intr)
        sm.insert_component(peripheral, d1)
        sm.insert_component(peripheral, d2)
        sm.insert_component(memory, m1)
        sm.insert_component(memory, m2)
        rom = generate_rom_image(sm)
        rom_in = sdbc.convert_rom_to_32bit_buffer(rom)
 
        #print_sdb(rom)
        sm = parse_rom_image(rom_in)
        rom_out = generate_rom_image(sm)
        rom_out = sdbc.convert_rom_to_32bit_buffer(rom_out)
        #print_sdb_rom(rom_out)
        #compare_roms(rom_in, rom_out)
        self.assertEqual(rom_in, rom_out)

    def test_generate_one_sub_bus_with_url(self):
        sm = som.SOM()
        sm.initialize_root()
        root = sm.get_root()
        peripheral = sm.insert_bus()
        peripheral.set_name("peripheral")
        memory = sm.insert_bus()
        memory.set_name("memory")
        d1 = sdbc.create_device_record(name = "device 1", size = 0x100)
        d2 = sdbc.create_device_record(name = "device 2", size = 0x100)
        m1 = sdbc.create_device_record(name = "memory 1", size = 0x10000)
        m2 = sdbc.create_device_record(name = "memory 2", size = 0x20000)
        intr = sdbc.create_integration_record("Integration Data",
                                                vendor_id = 0x800BEAF15DEADC03,
                                                device_id = 0x00000000)
        url = sdbc.create_repo_url_record("http://www.geocities.com")
        synthesis = sdbc.create_synthesis_record("Synthesis Name", 123, "cool tool", 1.0, "jeff")
        sm.insert_component(root, url)
        sm.insert_component(root, synthesis)

        peripheral.set_child_spacing(0x0100000000)
        sm.insert_component(peripheral, intr)
        sm.insert_component(peripheral, d1)
        sm.insert_component(peripheral, d2)
        sm.insert_component(memory, m1)
        sm.insert_component(memory, m2)
        rom = generate_rom_image(sm)
        rom_in = sdbc.convert_rom_to_32bit_buffer(rom)
 
        #print_sdb(rom)
        sm = parse_rom_image(rom_in)
        rom_out = generate_rom_image(sm)
        rom_out = sdbc.convert_rom_to_32bit_buffer(rom_out)
        #print_sdb_rom(rom_out)
        #compare_roms(rom_in, rom_out)
        self.assertEqual(rom_in, rom_out)




def compare_roms(rom_in, rom_out):
    if len(rom_in) != len(rom_out):
        print "Length of rom is not equal!"
        return

    rom_in = rom_in.splitlines()
    rom_out = rom_out.splitlines()
    for i in range (0, len(rom_in), 4):
        if (i % 16 == 0):
            magic = "0x%s" % (rom_in[i].lower())
            last_val = int(rom_in[i + 15], 16) & 0xFF
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

        if rom_in[i] == rom_out[i] and rom_in[i + 1] == rom_out[i + 1] and rom_in[i + 2] == rom_out[i + 2] and rom_in[i + 3] == rom_out[i + 3]:
            print "%s %s : %s %s" % (rom_in[i], rom_in[i + 1], rom_in[i + 2], rom_in[i + 3])
        else:
            print "%s %s : %s %s != %s %s : %s %s" % (rom_in[i], rom_in[i + 1], rom_in[i + 2], rom_in[i + 3], rom_out[i], rom_out[i + 1], rom_out[i + 2], rom_out[i + 3])






def print_sdb_rom(rom):
    #rom = sdbc.convert_rom_to_32bit_buffer(rom)
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




ROM1 =  "5344422D\n"\
        "00010100\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000100\n"\
        "80000000\n"\
        "0000C594\n"\
        "00000001\n"\
        "00000001\n"\
        "140F0105\n"\
        "746F7000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000207\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000100\n"\
        "80000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "140F0105\n"\
        "64657669\n"\
        "63652031\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "000000FF"

ROM2 =  "5344422D\n"\
        "00020100\n"\
        "00000000\n"\
        "00000000\n"\
        "03000000\n"\
        "00000000\n"\
        "80000000\n"\
        "0000C594\n"\
        "00000001\n"\
        "00000001\n"\
        "140F0105\n"\
        "746F7000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000020\n"\
        "00000000\n"\
        "00000000\n"\
        "00000100\n"\
        "00000000\n"\
        "80000000\n"\
        "0000C594\n"\
        "00000001\n"\
        "00000001\n"\
        "140F0105\n"\
        "70657269\n"\
        "70686572\n"\
        "616C0000\n"\
        "00000000\n"\
        "00000002\n"\
        "00000000\n"\
        "00000040\n"\
        "00000100\n"\
        "00000000\n"\
        "00000200\n"\
        "00030000\n"\
        "80000000\n"\
        "0000C594\n"\
        "00000001\n"\
        "00000001\n"\
        "140F0105\n"\
        "6D656D6F\n"\
        "72790000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000002\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "000000FF\n"\
        "5344422D\n"\
        "00020100\n"\
        "00000000\n"\
        "00000000\n"\
        "00000100\n"\
        "00000000\n"\
        "80000000\n"\
        "0000C594\n"\
        "00000001\n"\
        "00000001\n"\
        "140F0105\n"\
        "70657269\n"\
        "70686572\n"\
        "616C0000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000207\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000100\n"\
        "80000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "140F0105\n"\
        "64657669\n"\
        "63652031\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "00000000\n"\
        "00000207\n"\
        "00000001\n"\
        "00000000\n"\
        "00000003\n"\
        "00000100\n"\
        "80000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "140F0105\n"\
        "64657669\n"\
        "63652032\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "000000FF\n"\
        "5344422D\n"\
        "00020100\n"\
        "00000100\n"\
        "00000000\n"\
        "00000200\n"\
        "00030000\n"\
        "80000000\n"\
        "0000C594\n"\
        "00000001\n"\
        "00000001\n"\
        "140F0105\n"\
        "6D656D6F\n"\
        "72790000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000207\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00010000\n"\
        "80000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "140F0105\n"\
        "6D656D6F\n"\
        "72792031\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "00000000\n"\
        "00000207\n"\
        "00000000\n"\
        "00010000\n"\
        "00000000\n"\
        "00030000\n"\
        "80000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "140F0105\n"\
        "6D656D6F\n"\
        "72792032\n"\
        "00000000\n"\
        "00000000\n"\
        "00000001\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "00000000\n"\
        "000000FF"
