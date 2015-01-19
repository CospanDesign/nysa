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

from sdb import SDB
from sdb import SDBInfo
from sdb import SDBError

SDB_INTERCONNECT_MAGIC  = 0x5344422D
SDB_BUS_TYPE_WISHBONE   = 0x00
SDB_BUS_TYPE_STORAGE    = 0x01

class SDBROMError(Exception):
    pass

class SDBROM(object):

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
        self.rom = {}

    def __len__(self):
        #each element is 64 bytes long
        return (len(self.rom) / 64)

    def parse_rom(self, buf, debug = False):
        self.rom = Array('B')
        for i in range(0, len(buf), 2):
            self.rom.append(int(buf[i:i+2], 16))

        try:
            for i in range(0, (len(self.rom) / 64)):
                #if debug: print "i: %d" % i
                self._parse_rom_element(self.rom[i * 64: (i + 1) * 64], debug)
        except SDBError as err:
            print "SDB Error: %s" % str(err)
        except SDBInfo as inf:
            if debug: print "Reached end of SDB"

    def _parse_rom_element(self, element_buffer, debug = False):
        sdb = SDB()
        sdb.parse_rom_element(element_buffer, debug)
        if sdb.is_interconnect():
            if debug: print "Interconnect: %s" % sdb.d["SDB_NAME"]
            if debug: print "\tNumber of Elements: %d" % sdb.get_number_of_records_as_int()

        elif sdb.is_device():
            if debug: print "Device: %s" % sdb.d["SDB_NAME"]

        elif sdb.is_bridge():
            if debug: print "Bridge: %s" % sdb.d["SDB_NAME"]

        if debug: print "\t0x%016X - 0x%016X: Size: 0x%016X" % (sdb.get_start_address_as_int(), \
                                                                sdb.get_end_address_as_int(), \
                                                                sdb.get_size_as_int())




