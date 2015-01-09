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
    -Changed the D R T size from 4 to 8
07/17/2013
    -Added license
"""

#gen_sdb.py
import sys
import os
import json
from string import Template
import copy

from gen import Gen
from nysa.cbuilder.sdb import SDB
from nysa.cbuilder.sdb import convert_rom_to_32bit_buffer
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

def calculate_sdb_size(tags):
    #Add 3 initially for the main interconnect
    #peripheral interconnect
    #memory interconnect
    count = 3
    #Two more for the bridges that tell the top where the peripheral and memory
    #interconnects are located
    count += 2
    #Add one more for the SDB
    count += 1
    count += len(tags["SLAVES"])
    count += len(tags["MEMORY"])
    #Empty Buffer at the end
    count += 1 
    count = (512 / 32) * count
    return count

class GenSDB(Gen):
    """Generate the SDB ROM"""

    def __init__(self):
        #print "in GenSDB"
        return

    def gen_script(self, tags = {}, buf = "", user_paths = [], debug = False):
        buf = ""
        tags = copy.deepcopy(tags)
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

        self.sdb = SDB()

        #Generate the main interconnect ROM
        self.sdb.parse_buffer(MAIN_INTERCONNECT)
        #self.sdb.d["SDB_DEVICE_ID"] = hex(board_id)
        self.sdb.d["SDB_DEVICE_ID"] = hex(image_id << 16 | board_id)
        self.sdb.set_start_address(0x00000000)
        self.sdb.set_size(0x200000000)
        #Indicate there are two sub interconnects
        self.sdb.set_number_of_records(2)
        rom = self.sdb.generate_interconnect_rom()
        buf = convert_rom_to_32bit_buffer(rom)
        buf += "\n"

        #Generate the Bridge for Peripherals
        self.sdb.set_start_address(0x00000000)
        self.sdb.set_size(0x100000000)
        self.sdb.d["SDB_NAME"] = "Peripherals Bridge"
        self.sdb.set_bridge_address(0x00000000)
        rom = self.sdb.generate_bridge_rom()
        buf += convert_rom_to_32bit_buffer(rom)
        buf += "\n"

        #Generate the peripheral Interconnect
        self.sdb.set_start_address(0x00000000)
        self.sdb.set_size(0x100000000)
        self.sdb.set_number_of_records(len(tags["SLAVES"]) + 1)
        self.sdb.d["SDB_NAME"] = "Peripherals Bus"
        rom = self.sdb.generate_interconnect_rom()
        buf += convert_rom_to_32bit_buffer(rom)
        buf += "\n"

        #Generate SDB Device
        self.sdb.d["SDB_NAME"] = "SDB"
        self.sdb.set_start_address(0x00)
        self.sdb.set_size(calculate_sdb_size(tags))
        self.sdb.d["SDB_ABI_VERSION_MAJOR"] = "0x0000"
        self.sdb.d["SDB_ABI_VERSION_MAJOR"] = "0x0000"
        rom = self.sdb.generate_device_rom()
        buf += convert_rom_to_32bit_buffer(rom)
        buf += "\n"

        offset = 0x01000000
        #Process the slave elements
        for i in range (0, len(tags["SLAVES"])):
            key = tags["SLAVES"].keys()[i]
            name = tags["SLAVES"][key]["filename"]
            absfilename = utils.find_rtl_file_location(name, self.user_paths)
            f = open(absfilename, 'r')
            slave_buffer = f.read()
            f.close()
            self.sdb.parse_buffer(slave_buffer)
            offset = 0x01000000 * (i + 1)
            self.sdb.set_start_address(offset)

            rom = self.sdb.generate_device_rom()
            buf += convert_rom_to_32bit_buffer(rom)
            buf += "\n"

        #Generate the Bridge for Memory
        self.sdb.set_start_address(0x10000000)
        self.sdb.set_size(0x200000000)
        self.sdb.d["SDB_NAME"] = "Memory Bridge"
        self.sdb.set_bridge_address(0x10000000)
        rom = self.sdb.generate_bridge_rom()
        buf += convert_rom_to_32bit_buffer(rom)
        buf += "\n"


        #Generate the memory Interconnect
        self.sdb.set_start_address(0x000000000)
        self.sdb.set_size(0x100000000)
        self.sdb.set_number_of_records(len(tags["MEMORY"]))
        self.sdb.d["SDB_NAME"] = "Memory Bus"
        rom = self.sdb.generate_interconnect_rom()
        buf += convert_rom_to_32bit_buffer(rom)
        buf += "\n"

        #Process the memory elements
        mem_offset = 0
        for i in range (0, len(tags["MEMORY"])):
            key = tags["MEMORY"].keys()[i]
            name = tags["MEMORY"][key]["filename"]
            absfilename = utils.find_rtl_file_location(name, self.user_paths)
            f = open(absfilename, 'r')
            memory_buffer = f.read()
            f.close()
            self.sdb.parse_buffer(memory_buffer)
            self.sdb.set_start_address(mem_offset)
            mem_offset += self.sdb.get_size_as_int()

            rom = self.sdb.generate_device_rom()
            buf += convert_rom_to_32bit_buffer(rom)
            buf += "\n"

        rom = self.sdb.generate_empty_rom()
        buf += convert_rom_to_32bit_buffer(rom)

        return buf

    def gen_name(self):
        print "generate a ROM"
