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
from sdb_component import SDBComponent as sdbc
import sdb_component

from sdb_object_model import SOMBus

from sdb import SDBInfo
from sdb import SDBWarning
from sdb import SDBError
from sdb_component import SDB_INTERCONNECT_MAGIC
from sdb_component import SDB_ROM_RECORD_LENGTH as RECORD_LENGTH

#Public facing functions
def generate_rom_image(som):
    """
    Given a populated SOM generate a ROM image

    Args:
        som (SDBObjectModel): A populated SOM

    Return:
        Nothing

    Raises:
        SDBError, error while parsing the SOM
    """
    rom = Array('B')
    #Go through each of the elements.
    root = som.get_root()
    return _bus_to_rom(root, rom)

#Private functions (SDB -> ROM)
def _bus_to_rom(bus, rom, addr = None):
    """
    Parse a bus, starting with the actual interconnect and then all the
    way through the final device, this stores the busses to be processed
    later and putting a birdge in the spot where the new bus will be
    """
    buses = []
    bridge_address_offset = 0x00
    if addr is None:
        addr = 0x00

    #Generate a slice of the ROM that will contain the entire bus
    #Add 1 for the initial interconnect
    #Add 1 for the empty block afterwards
    #print "Total length: %d" % (len(bus) + 2)
    #print "Total byte length: %d" % (RECORD_LENGTH * (len(bus) + 2) / 8)

    for i in range((len(bus) + 2) * RECORD_LENGTH):
        rom.append(0x00)

    #Put in a marker for an empty buffer
    rom[len(rom) - 1] = 0xFF

    _generate_interconnect_rom(bus.get_component(), rom, addr)
    addr += RECORD_LENGTH

    pos = 0
    for entity in bus:
        #print "At position: %d" % pos
        pos += 1
        if isinstance(entity, SOMBus):
            _generate_bridge_rom(entity.get_component(), rom, addr)
            _bus_to_rom(entity, rom, len(rom))
        else:
            _generate_entity_rom(entity.get_component(), rom, addr)

        addr += RECORD_LENGTH
    return rom

def _generate_entity_rom(entity, rom, addr):
    """
    Call this function with anything besides a bridge or an interconnect
    """
    if entity.is_device():
        _generate_device_rom(entity, rom, addr)
    elif entity.is_integration_record():
        _generate_integration_rom(entity, rom, addr)
    elif entity.is_url_record():
        _generate_url_rom(entity, rom, addr)
    elif entity.is_synthesis_record():
        _generate_synthesis_rom(entity, rom, addr)

def _generate_bridge_rom(entity, rom, addr):
    _generate_product_rom(entity, rom, addr)
    _generate_component_rom(entity, rom, addr)

    offset = len(rom) / 8
    #addr = entity.get_bridge_child_addr_as_int()
    #print "Address: 0x%016X" % addr
    rom[addr + 0x00] = (offset >> 56) & 0xFF
    rom[addr + 0x01] = (offset >> 48) & 0xFF
    rom[addr + 0x02] = (offset >> 40) & 0xFF
    rom[addr + 0x03] = (offset >> 32) & 0xFF
    rom[addr + 0x04] = (offset >> 24) & 0xFF
    rom[addr + 0x05] = (offset >> 16) & 0xFF
    rom[addr + 0x06] = (offset >> 8 ) & 0xFF
    rom[addr + 0x07] = (offset >> 0 ) & 0xFF
    rom[addr + RECORD_LENGTH - 1] = sdb_component.SDB_RECORD_TYPE_BRIDGE

def _generate_interconnect_rom(entity, rom, addr):
    _generate_product_rom(entity, rom, addr)
    _generate_component_rom(entity, rom, addr)
    rom[addr + 0x00] = (SDB_INTERCONNECT_MAGIC >> 24) & 0xFF
    rom[addr + 0x01] = (SDB_INTERCONNECT_MAGIC >> 16) & 0xFF
    rom[addr + 0x02] = (SDB_INTERCONNECT_MAGIC >> 8 ) & 0xFF
    rom[addr + 0x03] = (SDB_INTERCONNECT_MAGIC >> 0 ) & 0xFF

    nrecs = entity.get_number_of_records_as_int()
    rom[addr + 0x04] = (nrecs >> 8) & 0xFF
    rom[addr + 0x05] = (nrecs >> 0) & 0xFF

    version = entity.get_version_as_int()
    rom[addr + 0x06] = version & 0xFF

    bus_type = entity.get_bus_type_as_int()
    rom[addr + 0x07] = bus_type & 0xFF
    rom[addr + RECORD_LENGTH - 1] = entity.get_module_record_type()

def _generate_device_rom(entity, rom, addr):
    _generate_product_rom(entity, rom, addr)
    _generate_component_rom(entity, rom, addr)

    #ABI Class
    abi_class = entity.get_abi_class_as_int()
    rom[addr + 0x00] = (abi_class >> 8) & 0xFF
    rom[addr + 0x01] = (abi_class) & 0xFF

    #abi version major
    abi_major = entity.get_abi_version_major_as_int()
    rom[addr + 0x02] = (abi_major & 0xFF)

    #ABI version minor
    abi_minor = entity.get_abi_version_minor_as_int()
    rom[addr + 0x03] = (abi_minor & 0xFF)

    #Bus Specific Stuff
    endian = entity.get_endian_as_int()
    bus_width = entity._translate_buf_width_to_rom_version()
    executable = 0
    writeable = 0
    readable = 0

    if entity.is_executable():
        executable = 1
    if entity.is_writeable():
        writeable = 1
    if entity.is_readable():
        readable = 1

    #print "executable: %s" % str(executable)
    #print "writeable: %s" % str(writeable)
    #print "readable: %s" % str(readable)

    rom[addr + 0x04] = 0
    rom[addr + 0x05] = 0
    rom[addr + 0x06] = bus_width
    rom[addr + 0x07] = (endian << 4 | executable << 2 | writeable << 1 | readable)

    rom[addr + RECORD_LENGTH - 1] = entity.get_module_record_type()

def _generate_integration_rom(entity, rom, addr):
    for i in range(0x1F):
        rom[addr + i] = 0x00
    _generate_product_rom(entity, rom, addr)
    rom[addr + RECORD_LENGTH - 1] = entity.get_module_record_type()

def _generate_url_rom(entity, rom, addr):
    url = entity.get_url()
    _string_to_rom(url, RECORD_LENGTH - 1, rom, addr)
    rom[addr + RECORD_LENGTH - 1] = entity.get_module_record_type()

def _generate_synthesis_rom(entity, rom, addr):

    _string_to_rom(entity.get_synthesis_name(), 0x10, rom, addr)
    _string_to_rom(entity.get_synthesis_commit_id(),      0x10, rom, addr + 0x10)
    _string_to_rom(entity.get_synthesis_tool_name(),      0x08, rom, addr + 0x20)
    _string_to_rom(entity.get_synthesis_tool_version(),   0x08, rom, addr + 0x28)
    #Date
    year, month, day = entity.get_date_as_int()
    rom[addr + 0x2C] = int(year   / 100)
    rom[addr + 0x2D] = int(year   % 100)
    rom[addr + 0x2E] = (month       )
    rom[addr + 0x2F] = (day         )
    _string_to_rom(entity.get_name(),           0x0F, rom, addr + 0x34)
    rom[addr + RECORD_LENGTH - 1] = entity.get_module_record_type()

def _generate_product_rom(entity, rom, addr):

    #Vendor ID
    vendor_id = entity.get_vendor_id_as_int()
    rom[addr + 0x18] = (vendor_id >> 56) & 0xFF
    rom[addr + 0x19] = (vendor_id >> 48) & 0xFF
    rom[addr + 0x1A] = (vendor_id >> 40) & 0xFF
    rom[addr + 0x1B] = (vendor_id >> 32) & 0xFF
    rom[addr + 0x1C] = (vendor_id >> 24) & 0xFF
    rom[addr + 0x1D] = (vendor_id >> 16) & 0xFF
    rom[addr + 0x1E] = (vendor_id >> 8 ) & 0xFF
    rom[addr + 0x1F] = (vendor_id >> 0 ) & 0xFF

    #Device ID
    device_id = entity.get_device_id_as_int()
    rom[addr + 0x20] = (device_id >> 24) & 0xFF
    rom[addr + 0x21] = (device_id >> 16) & 0xFF
    rom[addr + 0x22] = (device_id >>  8) & 0xFF
    rom[addr + 0x23] = (device_id >>  0) & 0xFF

    #Version
    version = entity.get_core_version_as_int()
    rom[addr + 0x24] = (version >> 24) & 0xFF
    rom[addr + 0x25] = (version >> 16) & 0xFF
    rom[addr + 0x26] = (version >>  8) & 0xFF
    rom[addr + 0x27] = (version >>  0) & 0xFF

    #Date
    year, month, day = entity.get_date_as_int()
    rom[addr + 0x28] = int(year   / 100)
    rom[addr + 0x29] = int(year   % 100)
    rom[addr + 0x2A] = (month       )
    rom[addr + 0x2B] = (day         )

    #Name
    _string_to_rom(entity.get_name(), 19, rom, addr + 0x2C)

def _generate_component_rom(entity, rom, addr):
    address_first = Array('B')
    address_last = Array('B')
    start_address = entity.get_start_address_as_int()
    end_address = entity.get_end_address_as_int()
    for i in range (0, RECORD_LENGTH, 8):
        address_first.append((start_address >> (56 - i) & 0xFF))
        address_last.append((end_address >> (56 - i) & 0xFF))

    rom[addr + 0x08] = address_first[0]
    rom[addr + 0x09] = address_first[1]
    rom[addr + 0x0A] = address_first[2]
    rom[addr + 0x0B] = address_first[3]
    rom[addr + 0x0C] = address_first[4]
    rom[addr + 0x0D] = address_first[5]
    rom[addr + 0x0E] = address_first[6]
    rom[addr + 0x0F] = address_first[7]

    rom[addr + 0x10] = address_last[0]
    rom[addr + 0x11] = address_last[1]
    rom[addr + 0x12] = address_last[2]
    rom[addr + 0x13] = address_last[3]
    rom[addr + 0x14] = address_last[4]
    rom[addr + 0x15] = address_last[5]
    rom[addr + 0x16] = address_last[6]
    rom[addr + 0x17] = address_last[7]

def _string_to_rom(s, max_length, rom, addr):
    if len(s) > max_length:
        s = s[:max_length]
    s  = Array('B', s)

    for i in range(len(s)):
        rom[addr + i] = s[i]

