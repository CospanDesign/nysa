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

from datetime import datetime
from array import array as Array
import collections

from sdb import SDBInfo
from sdb import SDBWarning
from sdb import SDBError

import string

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

SDB_ROM_RECORD_LENGTH   = 64
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
        sdb.d["SDB_CORE_VERSION"] = core_version
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
        self.d["SDB_CORE_VERSION"] = "0.0.01"
        self.d["SDB_BRIDGE_CHILD_ADDR"] = "0"
        self.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTERCONNECT
        self.d["SDB_ABI_CLASS"] = hex(0x00)
        self.d["SDB_ABI_VERSION_MAJOR"] = hex(0x00)
        self.d["SDB_ABI_VERSION_MINOR"] = hex(0x00)
        self.d["SDB_VENDOR_ID"] = hex(0x8000000000000000)
        self.d["SDB_DEVICE_ID"] = hex(0x00000000)
        self.d["SDB_ABI_ENDIAN"] = "BIG"
        self.d["SDB_ABI_DEVICE_WIDTH"] = "32"
        self.d["SDB_EXECUTABLE"] = "True"
        self.d["SDB_WRITEABLE"] = "True"
        self.d["SDB_READABLE"] = "True"
        d = datetime.now()

        sd = "%04d/%02d/%02d" % (d.year, d.month, d.day)
        self.d["SDB_DATE"] = sd

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
        addr = long(addr)
        self.d["SDB_LAST_ADDRESS"] = hex(addr + self.get_size_as_int())

    def get_start_address_as_int(self):
        return long(self.d["SDB_START_ADDRESS"], 16)

    def set_size(self, size):
        self.d["SDB_SIZE"] = hex(size)
        start_addr = self.get_start_address_as_int()
        self.d["SDB_LAST_ADDRESS"] = hex(start_addr + self.get_size_as_int())

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
        return long(self.d["SDB_SIZE"], 0)

    def get_end_address_as_int(self):
        return long(self.d["SDB_LAST_ADDRESS"], 16)

    def get_vendor_id_as_int(self):
        return long(self.d["SDB_VENDOR_ID"], 16)

    def get_device_id_as_int(self):
        #print "device id: %s" % self.d["SDB_DEVICE_ID"]
        return int(self.d["SDB_DEVICE_ID"], 16)

    def get_abi_class_as_int(self):
        return int(self.d["SDB_ABI_CLASS"], 16)

    def get_abi_version_major_as_int(self):
        return long(self.d["SDB_ABI_VERSION_MAJOR"], 16)

    def get_abi_version_minor_as_int(self):
        return long(self.d["SDB_ABI_VERSION_MINOR"], 16)

    def get_endian_as_int(self):
        if string.upper(self.d["SDB_ABI_ENDIAN"]) == "LITTLE":
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
        #print "version string: %s" % self.d["SDB_CORE_VERSION"]
        version = 0
        version |= (0x0F & int(version_strings[0], 0)) << 24
        version |= (0x0F & int(version_strings[1], 0)) << 16
        version |= (0xFF & int(version_strings[2], 0))
        #print "Version output: %04d" % version
        #Base 10
        return version

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

    def get_url(self):
        return self.d["SDB_MODULE_URL"]

    def get_synthesis_name(self):
        return self.d["SDB_SYNTH_NAME"]

    def get_synthesis_commit_id(self):
        return self.d["SDB_SYNTH_COMMIT_ID"]

    def get_synthesis_tool_name(self):
        return self.d["SDB_SYNTH_TOOL_NAME"]

    def get_synthesis_tool_version(self):
        return self.d["SDB_SYNTH_TOOL_VER"]

    def get_synthesis_user_name(self):
        return self.d["SDB_SYNTH_USERNAME"]

    def get_version_as_int(self):
        return int (self.d["SDB_VERSION"])

    def set_bridge_child_addr(self, addr):
        self.d["SDB_BRIDGE_CHILD_ADDR"] = hex(addr)

    def get_bridge_child_addr_as_int(self):
        return int(self.d["SDB_BRIDGE_CHILD_ADDR"], 16)

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

    def get_module_record_type(self):
        return self.d["SDB_RECORD_TYPE"]

    def __str__(self):
        buf = ""
        buf += "SDB Component\n"
        buf += "\tName: %s\n" % self.d["SDB_NAME"]
        buf += "\tType: %s\n" % self.d["SDB_RECORD_TYPE"]
        buf += "\tSize: 0x%08X\n" % self.get_size_as_int()
        if self.is_interconnect():
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


