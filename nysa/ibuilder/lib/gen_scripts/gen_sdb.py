# Distributed under the MIT licesnse.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Changes:

01/07/2015
    -Changed from DRT to SDB
12/13/2011
    -Changed the response from 25 characters to 32
12/02/2011
    -Changed the DRT size from 4 to 8
07/17/2013
    -Added license
"""

#gen_sdb.py
import sys
import os
import json
from string import Template
import copy
from collections import OrderedDict

from gen import Gen
from nysa.cbuilder import sdb_component as sdbc
from nysa.cbuilder import sdb_object_model as som
from nysa.cbuilder import som_rom_generator as srg
from nysa.cbuilder import device_manager

from nysa.cbuilder.sdb import SDBError

from nysa.ibuilder.lib import utils

import nysa.ibuilder.lib.verilog_utils as vutils

MAIN_INTERCONNECT = \
    "  Set the Vendor ID (Hexidecimal 64-bit Number)\n" \
    "  SDB_VENDOR_ID:800000000000C594\n" \
    "\n" \
    "  Set the Product ID\n" \
    "  SDB_DEVICE_ID:0000\n" \
    "\n" \
    "  Set the Version of the core\n" \
    "  SDB_CORE_VERSION:00.000.001\n" \
    "\n" \
    "  Set the name of the core\n" \
    "  SDB_NAME:nysa\n" \
    "\n" \
    "  Set ABI Class\n" \
    "  SDB_ABI_CLASS:0000\n" \
    "    Undocumented Device\n" \
    "\n" \
    "  Set API Version Major\n" \
    "  SDB_ABI_VERSION_MAJOR:00\n" \
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
    "  SDB_MODULE_URL:http://www.wiki.cospandesign.com\n" \
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

'''
def calculate_sdb_size(tags):
    #Start out with one for the interconnect
    count = 1
    #Add a count for the SDB
    count += 1
    #Add all the peripehrals
    count += len(tags["SLAVES"])
    #Add all the memory slaves
    count += len(tags["MEMORY"])
    #Empty Buffer at the end

    #XXX: Need to add all integration values into this

    count += 1
    count = (512 / 32) * count
    return count

def calculate_number_of_devices(tags):
    #Add one for the SDB
    count = 1
    count += len(tags["SLAVES"])
    for slave in tags["SLAVES"]:
        if is_integration_required(tags["SLAVES"][slave]):
            count += 1
    count += len(tags["MEMORY"])
    return count
'''

def is_integration_required(slave_dict):
    if "integration" in slave_dict.keys():
        return True
    return False

def generate_integration_record(slave_tags, slave):
    SDB_OFFSET = 1
    integration_list = slave_tags[slave]["integration"]
    slave_list = slave_tags.keys()
    #print "slave list: %s" % str(slave_list)
    slave_pos = slave_list.index(slave) + SDB_OFFSET 
    integration_buffer = "%d:" % slave_pos

    #Create an integration buffer
    for s in integration_list:
        #print "\tslave: %s" % s
        pos = int(slave_list.index(s)) + SDB_OFFSET
        #print "\t\tPosition: %d" % pos
        integration_buffer += str(pos)
        if integration_list.index(s) != len(integration_list) - 1:
            integration_buffer += ","
    
    c = sdbc.create_integration_record(information = integration_buffer)
    return c

class GenSDB(Gen):
    """Generate the SDB ROM"""

    def __init__(self):
        #print "in GenSDB"
        self.rom_element_count = 0
        return

    def get_number_of_records(self, tags, user_paths, debug = False):
        rom = self.gen_script(tags = tags, user_paths = user_paths, debug = debug)
        return self.rom_element_count

    def gen_script(self, tags = {}, buf = "", user_paths = [], debug = False):
        rom = self.gen_rom(tags, buf, user_paths, debug)
        buf = sdbc.convert_rom_to_32bit_buffer(rom)
        return buf

    def gen_rom(self, tags = {}, buf = "", user_paths = [], debug = False):
        sm = self.gen_som(tags, buf, user_paths, debug)
        rom = srg.generate_rom_image(sm)
        return rom

    def gen_som(self, tags = {}, buf = "", user_paths = [], debug = False):
        tags = copy.deepcopy(tags)
        self.rom_element_count = 0
        if "MEMORY" not in tags:
            tags["MEMORY"] = {}

        self.user_paths = user_paths
        board_name = tags["board"].lower()
        if not utils.is_board_id_in_dict(board_name):
            utils.update_board_id_dict()

        board_id = utils.get_board_id(board_name)

        image_id = 0
        for key in tags.keys():
            if key.lower() == "image_id":
                image_id = tags[key]

        sm = som.SOM()
        sm.initialize_root()
        root = sm.get_root()
        #Add 1 for Root
        self.rom_element_count += 1

        peripheral = sm.insert_bus(root,
                                    name = "peripheral")
        memory = sm.insert_bus(     root,
                                    name = "memory")

        #Add one for SDB ROM
        self.rom_element_count += 1
        self.rom_element_count += 1
        version_major = device_manager.get_device_id_from_name("SDB")
        sdb_rom = sdbc.create_device_record(name = "SDB",
                                            version_major = version_major)

        #Add two for bridge and one extra for empty
        self.rom_element_count += 3

        #Peripheral Bus
        #Add one for interconnect
        self.rom_element_count += 1



        '''
        #Move all the platform peripherals to the front of the SDB Bus
        temp_unordered_platform_tags = {}
        temp_platform_tags = OrderedDict()
        temp_periph_tags = OrderedDict()
        minor_dict = {}
        peripheral_id = device_manager.get_device_id_from_name("platform")

        for key in tags["SLAVES"]:
            filename = tags["SLAVES"][key]["filename"]
            absfilename = utils.find_rtl_file_location(filename, self.user_paths)
            f = open(absfilename, 'r')
            slave_buffer = f.read()
            f.close()

            per = sdbc.create_device_record(name = key)
            per.parse_buffer(slave_buffer)

            if per.get_abi_version_major_as_int() == peripheral_id:
                minor = per.get_abi_version_minor_as_int()
                minor_dict[minor] = key
                temp_unordered_platform_tags[key] = tags["SLAVES"][key]
            else:
                temp_periph_tags[key] = tags["SLAVES"][key]

        if len(minor_dict.keys()) > 0:
            #Order the platforms in terms of their minor numbers
            ordered_keys = sorted(minor_dict.keys(), key=int)
            for okey in ordered_keys:
                key = minor_dict[okey]
                temp_platform_tags[key] = temp_unordered_platform_tags[key]
            
            #Add all the peripheral slaves
            for key in temp_periph_tags:
                temp_platform_tags[key] = temp_periph_tags[key]
            
            #Put the slaves back in the original dictionary
            tags["SLAVES"] = temp_platform_tags
        '''


        #Add one per peripheral
        for i in range (0, len(tags["SLAVES"])):
            key = tags["SLAVES"].keys()[i]

            if is_integration_required(tags["SLAVES"][key]):
                ir = generate_integration_record(tags["SLAVES"], key)
                #print "Inserting Integration record for: %s" % key
                sm.insert_component(peripheral, ir)

            filename = tags["SLAVES"][key]["filename"]
            absfilename = utils.find_rtl_file_location(filename, self.user_paths)
            f = open(absfilename, 'r')
            slave_buffer = f.read()
            f.close()

            per = sdbc.create_device_record(name = key)
            per.parse_buffer(slave_buffer)
            per.set_name(str(key))
            sm.insert_component(peripheral, per)
            self.rom_element_count += 1

        #Add one for empty
        self.rom_element_count += 1

        #Memory Bus
        #Add one for interconnect
        self.rom_element_count += 1

        #Add one per memory peripheral
        for i in range (0, len(tags["MEMORY"])):
            key = tags["MEMORY"].keys()[i]
            name = tags["MEMORY"][key]["filename"]
            absfilename = utils.find_rtl_file_location(name, self.user_paths)
            f = open(absfilename, 'r')
            memory_buffer = f.read()
            f.close()

            mem = sdbc.create_device_record(name = key)
            mem.parse_buffer(memory_buffer)
            mem.set_name(str(key))
            sm.insert_component(memory, mem)
            self.rom_element_count += 1

        #add one for empty
        self.rom_element_count += 1

        #TODO: add Add one for URL of repo ?? Maybe
        #TODO: add Add one for Synthesis Record
        self.rom_element_count += 1

        sdb_rom.set_size(self.rom_element_count * sdbc.SDB_ROM_RECORD_LENGTH)
        sm.insert_component(peripheral, sdb_rom, 0)

        #Generate the ROM image
        sm.set_child_spacing(root,       0x0100000000)
        sm.set_child_spacing(peripheral, 0x0001000000)
        return sm

    def gen_name(self):
        print "generate a ROM"

