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
import collections

from sdb import SDBInfo
from sdb import SDBWarning
from sdb import SDBError

DESCRIPTION = "SDB Component Parser and Generator"

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
DESCRIPTION_DICT["SDB_DATE"]                = "Set the date of module YYYY/MM/DD or date of image build for synth"
DESCRIPTION_DICT["SDB_EXECUTABLE"]          = "Device is executable"
DESCRIPTION_DICT["SDB_WRITEABLE"]           = "Device is writeable"
DESCRIPTION_DICT["SDB_READABLE"]            = "Device is readable"
DESCRIPTION_DICT["SDB_NRECS"]               = "Number of Records"
DESCRIPTION_DICT["SDB_VERSION"]             = "Version of SDB"
DESCRIPTION_DICT["SDB_BUS_TYPE"]            = "Bus Type: Wishbone, Storage"
DESCRIPTION_DICT["SDB_BRIDGE_CHILD_ADDR"]   = "Bridge Child SDB Address Location Relative to SDB (Hex)"
DESCRIPTION_DICT["SDB_START_ADDRESS"]       = "Start Address (Hex)"
DESCRIPTION_DICT["SDB_LAST_ADDRESS"]        = "Last Address (Hex)"
DESCRIPTION_DICT["SDB_SIZE"]                = "Number of Registers"
DESCRIPTION_DICT["SDB_SYNTH_NAME"]          = "Name of Synthesis Vendor (16 chars)"
DESCRIPTION_DICT["SDB_SYNTH_COMMIT_ID"]     = "Commit ID of build Hex"
DESCRIPTION_DICT["SDB_SYNTH_TOOL_NAME"]     = "Name of Synthesis Tool (16 chars)"
DESCRIPTION_DICT["SDB_SYNTH_TOOL_VER"]      = "Version of Synthesis Tool"
DESCRIPTION_DICT["SDB_SYNTH_USER_NAME"]     = "User name of the person who built image"
DESCRIPTION_DICT["SDB_RECORD_TYPE"]         = "Type of device"

SDB_INTERCONNECT_MAGIC  = 0x5344422D
SDB_BUS_TYPE_WISHBONE   = 0x00
SDB_BUS_TYPE_STORAGE    = 0x01

SDB_RECORD_TYPE_INTERCONNECT = 0x00
SDB_RECORD_TYPE_DEVICE       = 0x01
SDB_RECORD_TYPE_BRIDGE       = 0x02
SDB_RECORD_TYPE_INTEGRATION  = 0x80
SDB_RECORD_TYPE_REPO_URL     = 0x81
SDB_RECORD_TYPE_SYNTHESIS    = 0x82
SDB_RECORD_TYPE_EMPTY        = 0xFF

def create_device_record(   name = None,
                            vendor_id = None,
                            device_id = None,
                            core_version = None,
                            abi_class = None,
                            version_major = None,
                            version_minor = None,
                            size = None):
    sdb = SDBComponent()
    sdb.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_DEVICE
    if name is not None:
        sdb.d["SDB_NAME"] = name
    if vendor_id is not None:
        sdb.d["SDB_VENDOR_ID"] = hex(vendor_id)
    if device_id is not None:
        sdb.d["SDB_DEVICE_ID"] = hex(device_id)
    if core_version is not None:
        sdb.d["SDB_VERSION"] = core_version
    if abi_class is not None:
        sdb.d["SDB_ABI_CLASS"] = hex(abi_class)
    if version_major is not None:
        sdb.d["SDB_ABI_VERSION_MAJOR"] = hex(version_major)
    if version_minor is not None:
        sdb.d["SDB_ABI_VERSION_MINOR"] = hex(version_minor)
    if size is not None:
        sdb.set_size(size)
    return sdb

def create_interconnect_record( name = None,
                                vendor_id = None,
                                device_id = None,
                                start_address = None,
                                size = None):
    sdb = SDBComponent()
    sdb.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTERCONNECT
    if name is not None:
        sdb.d["SDB_NAME"] = name
    if vendor_id is not None:
        sdb.d["SDB_VENDOR_ID"] = hex(vendor_id)
    if device_id is not None:
        sdb.d["SDB_DEVICE_ID"] = hex(device_id)
    if start_address is not None:
        sdb.set_start_address(start_address)
    if size is not None:
        sdb.set_size(size)
    return sdb

def create_bridge_record(       name = None,
                                vendor_id = None,
                                device_id = None,
                                start_address = None,
                                size = None):
    sdb = SDBComponent()
    sdb.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_BRIDGE
    if name is not None:
        sdb.d["SDB_NAME"] = name
    if vendor_id is not None:
        sdb.d["SDB_VENDOR_ID"] = hex(vendor_id)
    if device_id is not None:
        sdb.d["SDB_DEVICE_ID"] = hex(device_id)
    if start_address is not None:
        sdb.set_start_address(start_address)
    if size is not None:
        sdb.set_size(size)
    return sdb

def create_integration_record(  information,
                                vendor_id = None,
                                device_id = None):
    sdb = SDBComponent()
    sdb.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTEGRATION
    sdb.d["SDB_NAME"] = information
    if vendor_id is not None:
        sdb.d["SDB_VENDOR_ID"] = hex(vendor_id)
    if device_id is not None:
        sdb.d["SDB_DEVICE_ID"] = hex(device_id)
    return sdb

def create_synthesis_record(synthesis_name,
                      commit_id,
                      tool_name,
                      tool_version,
                      user_name):
    sdb = SDBComponent()
    sdb.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_SYNTHESIS
    sdb.d["SDB_SYNTH_NAME"] = synthesis_name
    if isinstance(commit_id, int):
        commit_id = hex(commit_id)
    sdb.d["SDB_SYNTH_COMMIT_ID"] = commit_id
    sdb.d["SDB_SYNTH_TOOL_NAME"] = tool_name
    if not isinstance(tool_version, str):
        tool_version = str(tool_version)
    sdb.d["SDB_SYNTH_TOOL_VER"] = tool_version
    sdb.d["SDB_SYNTH_USER_NAME"] = user_name
    return sdb

def create_repo_url_record(url):
    sdb = SDBComponent()
    sdb.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_REPO_URL
    sdb.d["SDB_RECORD_REPO_URL"] = url
    return sdb

class SDBComponent (object):

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
        "SDB_LAST_ADDRESS",
        "SDB_SYNTH_NAME",
        "SDB_SYNTH_COMMIT_ID",
        "SDB_SYNTH_TOOL_NAME",
        "SDB_SYNTH_TOOL_VER",
        "SDB_SYNTH_USER_NAME",
        "SDB_RECORD_TYPE"
    ]

    def __init__(self):
        self.d = {}
        for e in self.ELEMENTS:
            self.d[e] = ""

        self.d["SDB_SIZE"] = hex(0)
        self.d["SDB_START_ADDRESS"] = "0x00"
        self.d["SDB_LAST_ADDRESS"] = "0x00"
        self.d["SDB_NRECS"] = "0"
        self.d["SDB_BUS_TYPE"] = "Wishbone"
        self.d["SDB_VERSION"] = str(self.SDB_VERSION)
        self.d["SDB_BRIDGE_CHILD_ADDR"] = "0"
        self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTERCONNECT

#ROM -> SDB
    def parse_rom_element(self, rom, debug = False):
        possible_magic = rom[0] << 24 | \
                         rom[1] << 16 | \
                         rom[2] <<  8 | \
                         rom[3] <<  0

        if (possible_magic == SDB_INTERCONNECT_MAGIC):
            #if debug: print "Found Interconnect!"
            self._parse_rom_interconnect_element(rom, debug)
            self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTERCONNECT

        elif rom[63] == SDB_RECORD_TYPE_DEVICE:
            self._parse_rom_device_element(rom, debug)
            self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_DEVICE
        elif rom[63] == SDB_RECORD_TYPE_BRIDGE:
            self._parse_rom_bridge_element(rom, debug)
            self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_BRIDGE
        elif rom[63] == SDB_RECORD_TYPE_INTEGRATION:
            self.d["SDB_RECORD_TYPE"] = SDB_RECORD_INTEGRATION
        elif rom[63] == SDB_RECORD_TYPE_REPO_URL:
            self.d["SDB_RECORD_TYPE"] = SDB_RECORD_REPO_URL
        elif rom[63] == SDB_RECORD_TYPE_SYNTHESIS:
           self.d["SDB_RECORD_TYPE"] = SDB_RECORD_SYNTHESIS
        elif rom[63] == SDB_RECORD_TYPE_EMPTY:
           self.d["SDB_RECORD_TYPE"] = SDB_RECORD_EMPTY
        else:
            raise SDBInfo("Info: Unrecognized Record: 0x%02X" % rom[63])

    def _parse_rom_device_element(self, rom, debug = False):
        self.d["SDB_ABI_CLASS"] = hex(  rom[0] <<  8 | \
                                        rom[1] <<  0)
        self.d["SDB_ABI_VERSION_MAJOR"] = hex(rom[2])
        self.d["SDB_ABI_VERSION_MINOR"] = hex(rom[3])
        bus_width = rom[6]
        endian = (rom[7] >> 4) & 0x01
        executable = (rom[7] >> 2) & 0x01
        writeable = (rom[7] >> 1) & 0x01
        readable = (rom[7] >> 0) & 0x01

        self.d["SDB_EXECUTABLE"] = (executable == 1)
        self.d["SDB_WRITEABLE"] = (writeable == 1)
        self.d["SDB_READABLE"] = (readable == 1)
        self.d["SDB_ABI_ENDIAN"] = (endian == 0)
        if (bus_width == 0):
            self.d["SDB_ABI_DEVICE_WIDTH"] = "8"
        elif (bus_width == 1):
            self.d["SDB_ABI_DEVICE_WIDTH"] = "16"
        elif (bus_width == 2):
            self.d["SDB_ABI_DEVICE_WIDTH"] = "32"
        elif (bus_width == 3):
            self.d["SDB_ABI_DEVICE_WIDTH"] = "64"

        if endian:
            self.d["SDB_ABI_ENDIAN"] = "Little"
        else:
            self.d["SDB_ABI_ENDIAN"] = "Big"

        self._parse_rom_component_element(rom, debug)

    def _parse_rom_bridge_element(self, rom, debug = False):
        self.d["SDB_BRIDGE_CHILD_ADDR"] = hex(self._convert_rom_to_int(rom[ 0: 8]))
        self._parse_rom_component_element(rom, debug)

    def _parse_rom_interconnect_element(self, rom, debug = False):
        self.d["SDB_NRECS"] = hex(rom[4] << 8 | \
                                  rom[5] << 0)
        #if debug: print "Number of Records: %d" % self.d["SDB_NRECS"]
        self.d["SDB_VERSION"] = rom[6]
        self.d["SDB_BUS_TYPE"] = rom[7]
        self._parse_rom_component_element(rom, debug)
        if rom[63] != 0x00:
            raise SDBError("Interconnect element record does not match type: 0x%02X" % rom[63])

    def _parse_rom_component_element(self, rom, debug = False):
        self.d["SDB_START_ADDRESS"] =   hex(self._convert_rom_to_int(rom[ 8:16]))
        self.d["SDB_LAST_ADDRESS"] =    hex(self._convert_rom_to_int(rom[16:24]))
        start_address = int(self.d["SDB_START_ADDRESS"], 16)
        end_address = int(self.d["SDB_LAST_ADDRESS"], 16)
        self.set_size(end_address - start_address)
        self._parse_rom_product_element(rom, debug)

    def _parse_rom_product_element(self, rom, debug = False):
        self.d["SDB_VENDOR_ID"] =       hex(self._convert_rom_to_int(rom[24:32]))
        self.d["SDB_DEVICE_ID"] =       hex(self._convert_rom_to_int(rom[32:36]))
        self.d["SDB_CORE_VERSION"] =    hex(self._convert_rom_to_int(rom[36:40]))
        self.d["SDB_DATE"] =            rom[40:44].tostring()
        self.d["SDB_NAME"] =            rom[44:63].tostring()

    def _parse_rom_url_element(self, rom, debug = False):
        self.d["SDB_MODULE_URL"] =      rom[0:63].tostring()

    def _parse_synthesis_element(self, rom, debug = False):
        self.d["SDB_SYNTH_NAME"] =      rom[ 0:16].tostring()
        self.d["SDB_SYNTH_COMMIT_ID"] = rom[16:32].tostring()
        self.d["SDB_SYNTH_TOOL_NAME"] = rom[32:36].tostring()
        self.d["SDB_SYNTH_TOOL_VER"] =  rom[36:40].tostring()
        self.d["SDB_DATE"]       =      rom[40:48].tostring()
        self.d["SDB_SYNTH_USER_NAME"] = rom[48:63].tostring()
#Verilog Module -> SDB Device
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

#Verilog Module Template
    def generate_slave_template_buffer(self):
        buf = ""
        for e in self.ELEMENTS:
            buf += "%s\n" % DESCRIPTION_DICT[e]
            buf += "%s:%s\n\n" % (e, self.d[e])
        return buf

#SDB -> ROM
    def generate_bridge_rom(self):
        rom = Array('B')
        self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_BRIDGE
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
        rom[0x06] = (addr >> 8 ) & 0xFF
        rom[0x07] = (addr >> 0 ) & 0xFF

        rom[0x3F] = SDB_RECORD_TYPE_BRIDGE
        return rom

    def generate_interconnect_rom(self):
        self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTERCONNECT
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
        rom[0x3F] = SDB_RECORD_TYPE_INTERCONNECT
        return rom

    def generate_device_rom(self):
        self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_DEVICE
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

        rom[0x3F] = SDB_RECORD_TYPE_DEVICE
        return rom

    def generate_informative_rom(self):
        self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTEGRATION
        rom = Array('B')
        for i in range(64):
            rom.append(0x00)
        for i in range(0x1F):
            rom[i] = 0x00
        rom = self._generate_product_rom(rom)
        return rom


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
        device_id = self.get_device_id_as_int()
        rom[0x20] = (device_id >> 24) & 0xFF
        rom[0x21] = (device_id >> 16) & 0xFF
        rom[0x22] = (device_id >>  8) & 0xFF
        rom[0x23] = (device_id >>  0) & 0xFF

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

    def generate_empty_rom(self):
        rom = Array('B')
        for i in range(64):
            rom.append(0x00)
        return rom

#SDB -> Ordered Dict
    def generated_ordered_dict(self):
        od = collections.OrderedDict()
        for e in self.ELEMENTS:
            od[e] = self.d[e]
        return od

#Utility Functions
    def set_bridge_address(self, addr):
        self.d["SDB_BRIDGE_CHILD_ADDR"] = hex(addr)

    def get_bridge_address_as_int(self):
        return int(self.d["SDB_BRIDGE_CHILD_ADDR"], 16)

    def set_start_address(self, addr):
        """
        Sets the start address of the entity

        Args:
            addr (integer) start address

        Return:
            Nothing

        Raises:
            Nothing
        """
        self.d["SDB_START_ADDRESS"] = hex(addr)
        self.d["SDB_LAST_ADDRESS"] = hex(addr + int(self.d["SDB_SIZE"], 0))

    def get_start_address_as_int(self):
        return int(self.d["SDB_START_ADDRESS"], 16)

    def set_size(self, size):
        self.d["SDB_SIZE"] = hex(size)
        start_addr = int(self.d["SDB_START_ADDRESS"], 16)
        self.d["SDB_LAST_ADDRESS"] = hex(start_addr + int(self.d["SDB_SIZE"], 0))

    def set_number_of_records(self, nrecs):
        self.d["SDB_NRECS"] = str(nrecs)

    def get_number_of_records_as_int(self):
        return int(self.d["SDB_NRECS"], 16)

    def is_writeable(self):
        return (self.d["SDB_WRITEABLE"].lower() == "true")

    def enable_read(self, enable):
        self.d["SDB_READABLE"] = str(enable)

    def is_readable(self):
        return (self.d["SDB_READABLE"].lower() == "true")

    def set_name(self, name):
        self.d["SDB_NAME"] = name

    def get_name(self):
        return self.d["SDB_NAME"]

#Integer Rerpresentation of values
    def get_size_as_int(self):
        return int(self.d["SDB_SIZE"], 0)

    def get_end_address_as_int(self):
        return int(self.d["SDB_LAST_ADDRESS"], 16)

    def get_vendor_id_as_int(self):
        return int(self.d["SDB_VENDOR_ID"], 16)

    def get_device_id_as_int(self):
        #print "device id: %s" % self.d["SDB_DEVICE_ID"]
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

    def get_bus_type_as_int(self):
        if self.d["SDB_BUS_TYPE"].lower() == "wishbone":
            return 0
        elif self.d["SDB_BUS_TYPE"].lower() == "storage":
            return 1
        else:
            raise SDBError("Unknown Bus Type: %s" % self.d["SDB_BUS_TYPE"])

    def get_version_as_int(self):
        return int (self.d["SDB_VERSION"])

    def set_bridge_child_addr(self, addr):
        self.d["SDB_BRIDGE_CHILD_ADDR"] = hex(addr)

    def get_bridge_child_addr_as_int(self):
        return int(self.d["SDB_BRIDGE_CHILD_ADDR"], 16)

    def _convert_rom_to_int(self, rom):
        s = ""
        val = 0
        for i in range(len(rom)):
            val = val << 8 | rom[i]
            #print "val: 0x%016X" % val

        return val

    def is_device(self):
        if self.d["SDB_RECORD_TYPE"] == SDB_RECORD_TYPE_DEVICE:
            return True
        return False

    def is_interconnect(self):
        if self.d["SDB_RECORD_TYPE"] == SDB_RECORD_TYPE_INTERCONNECT:
            return True
        return False

    def is_bridge(self):
        if self.d["SDB_RECORD_TYPE"] == SDB_RECORD_TYPE_BRIDGE:
            return True
        return False

    def is_integration_record(self):
        if self.d["SDB_RECORD_TYPE"] == SDB_RECORD_TYPE_INTEGRATION:
            return True
        return False

    def is_url_record(self):
        if self.d["SDB_RECORD_TYPE"] == SDB_RECORD_TYPE_REPO_URL:
            return True
        return False

    def is_synthesis_record(self):
        if self.d["SDB_RECORD_TYPE"] == SDB_RECORD_TYPE_SYNTHESIS:
            return True
        return False

    def __str__(self):
        buf = ""
        buf += "SDB Component\n"
        buf += "\tName: %s\n" % self.d["SDB_NAME"]
        buf += "\tType: %s\n" % self.d["SDB_RECORD_TYPE"]
        buf += "\tSize: 0x%08X\n" % self.get_size_as_int()
        if is_interconnect():
            buf += "\tNum Devices: %d\n" % self.get_number_of_records_as_int()
            buf += "\tStart Address: 0x%010X\n" % self.get_start_address_as_int()
            buf += "\tEnd Address:   0x%010X\n" % self.get_end_address_as_int()
        return buf

def is_valid_bus_type(bus_type):
    if bus_type == "wishbone":
        return True
    if bus_type == "storage":
        return True
    return False

def convert_rom_to_32bit_buffer(rom):
    buf = ""
    last = False
    for i in range(0, len(rom), 4):
        if i + 4 >= len(rom):
            last = True
        buf += "%02X%02X%02X%02X" % (rom[i], rom[i + 1], rom[i + 2], rom[i + 3])
        if not last:
            buf += "\n"

    return buf


