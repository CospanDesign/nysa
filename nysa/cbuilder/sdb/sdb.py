#! /usr/bin/python

# Copyright (c) 2015 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa.
# (http://wiki.cospandesign.com/index.php?title=Nysa.org)
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.

from array import array as Array
import argparse
import collections


DESCRIPTION = "SDB Device Parser"
EPILOG = "Put Examples Here\n"

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION_DICT = collections.OrderedDict()
DESCRIPTION_DICT["SDB_VENDOR_ID"]           = "Set the Vendor ID (Hexidecimal 64-bit Number)"
DESCRIPTION_DICT["SDB_DEVICE_ID"]           = "Set the Device ID (Hexidecimal 32-bit Number)"
DESCRIPTION_DICT["SDB_CORE_VERSION"]        = "Set the Version of the core"
DESCRIPTION_DICT["SDB_NAME"]                = "Set the name of the core"
DESCRIPTION_DICT["SDB_ABI_CLASS"]           = "Class of the Device"
DESCRIPTION_DICT["SDB_ABI_VERSION_MAJOR"]   = "Set ABI Major Version"
DESCRIPTION_DICT["SDB_ABI_VERSION_MINOR"]   = "Set ABI Minor Version"
DESCRIPTION_DICT["SDB_ABI_ENDIAN"]          = "Set Endian (Big, Little)"
DESCRIPTION_DICT["SDB_ABI_DEVICE_WIDTH"]    = "Set Device Width (8 16 32 64)"
DESCRIPTION_DICT["SDB_MODULE_URL"]          = "Set the Module URL"
DESCRIPTION_DICT["SDB_DATE"]                = "Set the date of module YYYY/MM/DD"
DESCRIPTION_DICT["SDB_EXECUTABLE"]          = "Device is executable"
DESCRIPTION_DICT["SDB_WRITEABLE"]           = "Device is writeable"
DESCRIPTION_DICT["SDB_READABLE"]            = "Device is readable"
DESCRIPTION_DICT["SDB_NRECS"]               = "Number of Records"
DESCRIPTION_DICT["SDB_VERSION"]             = "Version of SDB"
DESCRIPTION_DICT["SDB_BUS_TYPE"]            = "Bus Type: Wishbone, Storage"
DESCRIPTION_DICT["SDB_BRIDGE_CHILD_ADDR"]   = "Bridge Child Address Location Relative to SDB (Hex)"
DESCRIPTION_DICT["SDB_START_ADDRESS"]       = "Start Address (Hex)"
DESCRIPTION_DICT["SDB_LAST_ADDRESS"]        = "Last Address (Hex)"
DESCRIPTION_DICT["SDB_SIZE"]                = "Number of Registers"

SDB_INTERCONNECT_MAGIC  = 0x5344422D
SDB_BUS_TYPE_WISHBONE   = 0x00
SDB_BUS_TYPE_STORAGE    = 0x01

class SDBError(Exception):
    pass

class SDB (object):

    SDB_VERSION = 1

    ELEMENTS = [
        "SDB_VENDOR_ID",
        "SDB_DEVICE_ID",
        "SDB_CORE_VERSION",
        "SDB_NAME",
        "SDB_ABI_CLASS",
        "SDB_ABI_VERSION_MAJOR",
        "SDB_ABI_VERSION_MINOR",
        "SDB_ABI_ENDIAN",
        "SDB_ABI_DEVICE_WIDTH",
        "SDB_MODULE_URL",
        "SDB_DATE",
        "SDB_EXECUTABLE",
        "SDB_READABLE",
        "SDB_WRITEABLE",
        "SDB_NRECS",
        "SDB_BUS_TYPE",
        "SDB_VERSION",
        "SDB_BRIDGE_CHILD_ADDR",
        "SDB_SIZE",
        "SDB_START_ADDRESS",
        "SDB_LAST_ADDRESS"
    ]

    def __init__(self):
        self.d = {}
        for e in self.ELEMENTS:
            self.d[e] = ""

        self.d["SDB_SIZE"] = 0
        self.d["SDB_START_ADDRESS"] = "0x00"
        self.d["SDB_LAST_ADDRESS"] = "0x00"
        self.d["SDB_NRECS"] = "0"
        self.d["SDB_BUS_TYPE"] = "Wishbone"
        self.d["SDB_VERSION"] = str(self.SDB_VERSION)
        self.d["SDB_BRIDGE_CHILD_ADDR"] = "0"

    def parse_buffer(self, in_buffer):
        #Seperate the buffer into a list of lines
        buffers = in_buffer.splitlines()
        for buf in buffers:
            for e in self.ELEMENTS:
                #Make this case insesitive
                if e.lower() in buf.lower():
                    value = buf.partition(":")[2]
                    value = value.strip()
                    self.d[e] = value

    def generate_slave_template_buffer(self):
        buf = ""
        for e in self.ELEMENTS:
            buf += "%s\n" % DESCRIPTION_DICT[e]
            buf += "%s:%s\n\n" % (e, self.d[e])
        return buf

    def _generate_product_rom(self, rom):

        #Vendor ID
        vendor_id = self.get_vendor_id_as_int()
        rom[0x18] = (vendor_id >> 56) & 0xFF
        rom[0x19] = (vendor_id >> 48) & 0xFF
        rom[0x1A] = (vendor_id >> 40) & 0xFF
        rom[0x1B] = (vendor_id >> 32) & 0xFF
        rom[0x1C] = (vendor_id >> 24) & 0xFF
        rom[0x1D] = (vendor_id >> 16) & 0xFF
        rom[0x1E] = (vendor_id >> 8 ) & 0xFF
        rom[0x1F] = (vendor_id >> 0 ) & 0xFF

        #Device ID
        product_id = self.get_device_id_as_int()
        rom[0x20] = (product_id >> 24) & 0xFF
        rom[0x21] = (product_id >> 16) & 0xFF
        rom[0x22] = (product_id >>  8) & 0xFF
        rom[0x23] = (product_id >>  0) & 0xFF

        #Version
        version = self.get_core_version_as_int()
        rom[0x24] = (version >> 24) & 0xFF
        rom[0x25] = (version >> 16) & 0xFF
        rom[0x26] = (version >>  8) & 0xFF
        rom[0x27] = (version >>  0) & 0xFF

        #Date
        year, month, day = self.get_date_as_int()
        rom[0x28] = int(year   / 100)
        rom[0x29] = int(year   % 100)
        rom[0x2A] = (month       )
        rom[0x2B] = (day         )

        #Name
        name = self.d["SDB_NAME"]
        if len(name) > 19:
            name = name[:19]

        na = Array('B', name) 
        for i in range(len(na)):
            rom[0x2C + i] = na[i]

        rom[0x3F] = 0x01
        return rom

    def _generate_component_rom(self, rom):
        address_first = Array('B')
        address_last = Array('B')
        start_address = self.get_start_address_as_int()
        end_address = self.get_end_address_as_int()
        for i in range (0, 64, 8):
            address_first.append((start_address >> (56 - i) & 0xFF))
            address_last.append((end_address >> (56 - i) & 0xFF))

        rom[0x08] = address_first[0]
        rom[0x09] = address_first[1]
        rom[0x0A] = address_first[2]
        rom[0x0B] = address_first[3]
        rom[0x0C] = address_first[4]
        rom[0x0D] = address_first[5]
        rom[0x0E] = address_first[6]
        rom[0x0F] = address_first[7]

        rom[0x10] = address_last[0]
        rom[0x11] = address_last[1]
        rom[0x12] = address_last[2]
        rom[0x13] = address_last[3]
        rom[0x14] = address_last[4]
        rom[0x15] = address_last[5]
        rom[0x16] = address_last[6]
        rom[0x17] = address_last[7]

        return rom

    def generate_bridge_rom(self):
        rom = Array('B')
        for i in range(64):
            rom.append(0x00)
        rom = self._generate_product_rom(rom)
        rom = self._generate_component_rom(rom)
        addr = self.get_bridge_child_addr_as_int()
        #print "Address: 0x%016X" % addr
        rom[0x00] = (addr >> 56) & 0xFF
        rom[0x01] = (addr >> 48) & 0xFF
        rom[0x02] = (addr >> 40) & 0xFF
        rom[0x03] = (addr >> 32) & 0xFF
        rom[0x04] = (addr >> 24) & 0xFF
        rom[0x05] = (addr >> 16) & 0xFF
        rom[0x06] = (addr >>  8) & 0xFF
        rom[0x07] = (addr >>  0) & 0xFF
        return rom

    def generate_interconnect_rom(self):
        rom = Array('B')
        for i in range(64):
            rom.append(0x00)

        rom = self._generate_product_rom(rom)
        rom = self._generate_component_rom(rom)
        rom[0x00] = (SDB_INTERCONNECT_MAGIC >> 24) & 0xFF
        rom[0x01] = (SDB_INTERCONNECT_MAGIC >> 16) & 0xFF
        rom[0x02] = (SDB_INTERCONNECT_MAGIC >> 8 ) & 0xFF
        rom[0x03] = (SDB_INTERCONNECT_MAGIC >> 0 ) & 0xFF

        nrecs = self.get_number_of_records_as_int()
        rom[0x04] = (nrecs >> 8) & 0xFF
        rom[0x05] = (nrecs >> 0) & 0xFF

        version = self.get_version_as_int()
        rom[0x06] = version & 0xFF

        bus_type = self.get_bus_type_as_int()
        rom[0x07] = bus_type & 0xFF

        return rom

    def generate_device_rom(self):
        rom = Array('B')
        for i in range(64):
            rom.append(0x00)

        rom = self._generate_product_rom(rom)
        rom = self._generate_component_rom(rom)

        #ABI Class
        abi_class = self.get_abi_class_as_int()
        rom[0x00] = (abi_class >> 8) & 0xFF
        rom[0x01] = (abi_class) & 0xFF

        #abi version major
        abi_major = self.get_abi_version_major_as_int()
        rom[0x02] = (abi_major & 0xFF)

        #ABI version minor
        abi_minor = self.get_abi_version_minor_as_int()
        rom[0x03] = (abi_minor & 0xFF)

        #Bus Specific Stuff
        endian = self.get_endian_as_int()
        bus_width = self._translate_buf_width_to_rom_version()
        executable = 0
        writeable = 0
        readable = 0

        if self.is_executable():
            executable = 1
        if self.is_writeable():
            writeable = 1 
        if self.is_readable():
            readable = 1

        #print "executable: %s" % str(executable)
        #print "writeable: %s" % str(writeable)
        #print "readable: %s" % str(readable)

        rom[0x04] = 0
        rom[0x05] = 0
        rom[0x06] = bus_width
        rom[0x07] = (endian << 4 | executable << 2 | writeable << 1 | readable)
        
        return rom

    def generated_ordered_dict(self):
        od = collections.OrderedDict()
        for e in self.ELEMENTS:
            od[e] = self.d[e]
        return od

    def set_start_address(self, addr):
        self.d["SDB_START_ADDRESS"] = hex(addr)
        self.d["SDB_LAST_ADDRESS"] = hex(addr + self.d["SDB_SIZE"])

    def get_start_address_as_int(self):
        return int(self.d["SDB_START_ADDRESS"], 16)

    def set_size(self, size):
        self.d["SDB_SIZE"] = size
        start_addr = int(self.d["SDB_START_ADDRESS"], 16)
        self.d["SDB_LAST_ADDRESS"] = hex(start_addr + self.d["SDB_SIZE"])

    def get_end_address_as_int(self):
        return int(self.d["SDB_LAST_ADDRESS"], 16)

    def get_vendor_id_as_int(self):
        return int(self.d["SDB_VENDOR_ID"], 16)

    def get_device_id_as_int(self):
        return int(self.d["SDB_DEVICE_ID"], 16)

    def get_abi_class_as_int(self):
        return int(self.d["SDB_ABI_CLASS"], 16)

    def get_abi_version_major_as_int(self):
        return int(self.d["SDB_ABI_VERSION_MAJOR"], 16)

    def get_abi_version_minor_as_int(self):
        return int(self.d["SDB_ABI_VERSION_MINOR"], 16)

    def get_endian_as_int(self):
        if self.d["SDB_ABI_ENDIAN"] == "LITTLE":
            return 1
        else:
            return 0
        
    def get_bus_width_as_int(self):
        return int(self.d["SDB_ABI_DEVICE_WIDTH"])

    def _translate_buf_width_to_rom_version(self):
        value = int(self.d["SDB_ABI_DEVICE_WIDTH"])
        if value == 8:
            return 0
        if value == 16:
            return 1
        if value == 32:
            return 2
        if value == 64:
            return 3
        raise SDBError("Unknown Device Width: %d" % value)

    def get_core_version_as_int(self):
        version_strings = self.d["SDB_CORE_VERSION"].split(".")
        version = ""
        for vs in version_strings:
            version += vs
        #Base 10
        return int(version)

    def get_date_as_int(self):
        date = self.d["SDB_DATE"]
        #print "date: %s" % date
        year = int(date[0:4])
        month = int(date[5:7])
        day = int(date[9:10])
        return year, month, day

    def enable_executable(self, enable):
        self.d["SDB_EXECUTABLE"] = str(enable)

    def is_executable(self):
        return (self.d["SDB_EXECUTABLE"].lower() == "true")

    def enable_write(self, enable):
        self.d["SDB_WRITEABLE"] = str(enable)

    def is_writeable(self):
        return (self.d["SDB_WRITEABLE"].lower() == "true")

    def enable_read(self, enable):
        self.d["SDB_READABLE"] = str(enable)

    def is_readable(self):
        return (self.d["SDB_READABLE"].lower() == "true")

    def get_bus_type_as_int(self):
        if self.d["SDB_BUS_TYPE"].lower() == "wishbone":
            return 0
        elif self.d["SDB_BUS_TYPE"].lower() == "storage":
            return 1
        else:
            raise SDBError("Unknown Bus Type: %s" % self.d["SDB_BUS_TYPE"])

    def get_version_as_int(self):
        return int (self.d["SDB_VERSION"])

    def set_number_of_records(self, nrecs):
        self.d["SDB_NRECS"] = str(nrecs)

    def get_number_of_records_as_int(self):
        return int(self.d["SDB_NRECS"], 16)

    def set_bridge_child_addr(self, addr):
        self.d["SDB_BRIDGE_CHILD_ADDR"] = hex(addr)

    def get_bridge_child_addr_as_int(self):
        return int(self.d["SDB_BRIDGE_CHILD_ADDR"], 16)
            
def convert_rom_to_32bit_buffer(rom):
    buf = ""
    for i in range(0, len(rom), 4):
        buf += "%02X%02X%02X%02X\n" % (rom[i], rom[i + 1], rom[i + 2], rom[i + 3])

    return buf

