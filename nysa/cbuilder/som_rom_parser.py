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

from sdb_object_model import SOM
from sdb_object_model import SOMBus

from sdb import SDBInfo
from sdb import SDBWarning
from sdb import SDBError

from sdb_component import SDB_INTERCONNECT_MAGIC
from sdb_component import SDB_ROM_RECORD_LENGTH as RECORD_LENGTH
from sdb_component import SDB_RECORD_TYPE_INTERCONNECT
from sdb_component import SDB_RECORD_TYPE_DEVICE
from sdb_component import SDB_RECORD_TYPE_BRIDGE
from sdb_component import SDB_RECORD_TYPE_INTEGRATION
from sdb_component import SDB_RECORD_TYPE_REPO_URL
from sdb_component import SDB_RECORD_TYPE_SYNTHESIS
from sdb_component import SDB_RECORD_TYPE_EMPTY




#Public Facing Functions
def parse_rom_image(rom):
    if isinstance(rom, str):
        lines = rom.splitlines()
        buf = ""
        for line in lines:
            buf += line
        rom = Array('B')
        for i in range(0, len(buf), 2):
            rom.append(int(buf[i:i + 2], 16))

    return _parse_bus(None, None, rom, addr = 0)

#Private Facing Functions
def _parse_bus(som, bus, rom, addr):
    """Recursive function used to parse a bus,
    when a sub bus is found then parse that bus
    """

    #This first element is a Known interconnect
    num_devices = 0
    if bus is None:
        #This is the top element
        som = SOM()
        som.initialize_root()
        bus = som.get_root()

    #print "Address: 0x%02X" % addr
    entity = parse_rom_element(rom, addr)
    if not entity.is_interconnect():
        raise SDBError("Rom data does not point to an interconnect")
    num_devices = entity.get_number_of_records_as_int()
    #print "entity: %s" % entity
    som.set_bus_component(bus, entity)

    #print "Number of entities to parse: %d" % num_devices
    #Get the spacing and size of each device for calculating spacing
    entity_size = []
    entity_addr_start = []
    #Add 1 to the number of devices so we account for the empty
    for i in range(1, (num_devices + 1)):
        #print "Working on %d" % i
        I = (i * RECORD_LENGTH) + addr
        entity = parse_rom_element(rom, I)

        #Gather spacing data to analyze later
        end = long(entity.get_end_address_as_int())
        start = long(entity.get_start_address_as_int())
        entity_addr_start.append(start)
        entity_size.append(end - start)

        if entity.is_bridge():
            #print "Found a bus: %s" % entity.get_name()
            #print "start: 0x%08X" % start
            sub_bus = som.insert_bus(root = bus,
                                     name = entity.get_name())

            #print "Bridge address: 0x%08X" % entity.get_bridge_address_as_int()
            #Set address as 2 X higher because SDB is using a 64 bit bus, but
            #ROM in FPGA is only 32 bits
            _parse_bus(som, sub_bus, rom, entity.get_bridge_address_as_int() * 8)
        else:
            #print "Found a non bus: %s" % entity.get_name()
            som.insert_component(root = bus,
                                 component = entity)

    spacing = 0
    prev_start = None
    prev_size = None
    for i in range(num_devices):
        #print "i: %d" % i
        size = entity_size[i]
        start_addr = entity_addr_start[i]
        #print "\tStart: 0x%08X" % start_addr
        if prev_start is None:
            prev_size = size
            prev_start = start_addr
            continue

        potential_spacing = (start_addr - prev_start)
        #print "\tPotential Spacing: 0x%08X" % potential_spacing
        #print "\tPrevious Size: 0x%08X" % prev_size
        if potential_spacing > prev_size:
            if potential_spacing > 0 and spacing == 0:
                #print "\t\tSpacing > 0"
                spacing = potential_spacing
            if spacing > potential_spacing:
                #print "\t\tSpacing: 0x%08X > 0x%08X" % (spacing, potential_spacing)
                spacing = potential_spacing

        prev_size = size
        prev_start = start_addr
       
    #print "\tspacing for %s: 0x%08X" % (bus.get_name(), spacing)
    #bus.set_child_spacing(spacing)
    som.set_child_spacing(bus, spacing)
    return som

#ROM -> SDB
def parse_rom_element(rom, addr = 0, debug = False):
    entity = sdbc()
    possible_magic = rom[addr + 0] << 24 | \
                     rom[addr + 1] << 16 | \
                     rom[addr + 2] <<  8 | \
                     rom[addr + 3] <<  0

    if (possible_magic == SDB_INTERCONNECT_MAGIC):
        #if debug: print "Found Interconnect!"
        _parse_rom_interconnect_element(entity, rom, addr, debug)
        entity.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTERCONNECT
    elif rom[addr + 63] == SDB_RECORD_TYPE_DEVICE:
        _parse_rom_device_element(entity, rom, addr, debug)
        entity.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_DEVICE
    elif rom[addr + 63] == SDB_RECORD_TYPE_BRIDGE:
        _parse_rom_bridge_element(entity, rom, addr, debug)
        entity.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_BRIDGE
    elif rom[addr + 63] == SDB_RECORD_TYPE_INTEGRATION:
        _parse_integration_element(entity, rom, addr, debug)
        entity.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_INTEGRATION
    elif rom[addr + 63] == SDB_RECORD_TYPE_REPO_URL:
        _parse_repo_url_element(entity, rom, addr, debug)
        entity.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_REPO_URL
    elif rom[addr + 63] == SDB_RECORD_TYPE_SYNTHESIS:
        _parse_synthesis_element(entity, rom, addr, debug)
        entity.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_SYNTHESIS
    elif rom[addr + 63] == SDB_RECORD_TYPE_EMPTY:
        entity.d["SDB_RECORD_TYPE"] = SDB_RECORD_TYPE_EMPTY
    else:
        raise SDBInfo("Info: Unrecognized Record: 0x%02X\nFull element: %s" % (rom[addr + 63], rom))
    return entity

def _parse_integration_element(entity, rom, addr, debug = False):
    _parse_rom_component_element(entity, rom, addr, debug)

def _parse_repo_url_element(entity, rom, addr, debug = False):
    entity.d["SDB_MODULE_URL"] = rom[addr:addr + RECORD_LENGTH - 1].tostring().strip("\0")

def _parse_rom_device_element(entity, rom, addr, debug = False):
    entity.d["SDB_ABI_CLASS"] = hex(  rom[addr + 0] <<  8 | \
                                    rom[addr + 1] <<  0)
    entity.d["SDB_ABI_VERSION_MAJOR"] = hex(rom[addr + 2])
    entity.d["SDB_ABI_VERSION_MINOR"] = hex(rom[addr + 3])
    bus_width = rom[addr + 6]
    endian = (rom[addr + 7] >> 4) & 0x01
    executable = (rom[addr + 7] >> 2) & 0x01
    writeable = (rom[addr + 7] >> 1) & 0x01
    readable = (rom[addr + 7] >> 0) & 0x01

    if executable:
        entity.d["SDB_EXECUTABLE"] = "True"
    else:
        entity.d["SDB_EXECUTABLE"] = "False" 

    if writeable:
        entity.d["SDB_WRITEABLE"] = "True"
    else:
        entity.d["SDB_WRITEABLE"] = "False"

    if readable:
        entity.d["SDB_READABLE"] = "True"
    else:
        entity.d["SDB_READABLE"] = "False"

    if endian:
        entity.d["SDB_ABI_ENDIAN"] = "Little"
    else:
        entity.d["SDB_ABI_ENDIAN"] = "Big"

    if (bus_width == 0):
        entity.d["SDB_ABI_DEVICE_WIDTH"] = "8"
    elif (bus_width == 1):
        entity.d["SDB_ABI_DEVICE_WIDTH"] = "16"
    elif (bus_width == 2):
        entity.d["SDB_ABI_DEVICE_WIDTH"] = "32"
    elif (bus_width == 3):
        entity.d["SDB_ABI_DEVICE_WIDTH"] = "64"

    if endian:
        entity.d["SDB_ABI_ENDIAN"] = "Little"
    else:
        entity.d["SDB_ABI_ENDIAN"] = "Big"

    _parse_rom_component_element(entity, rom, addr, debug)

def _parse_rom_bridge_element(entity, rom, addr, debug = False):
    entity.d["SDB_BRIDGE_CHILD_ADDR"] = hex(_convert_rom_to_int(rom[addr +  0:addr + 8]))
    _parse_rom_component_element(entity, rom, addr, debug)


def _parse_rom_interconnect_element(entity, rom, addr, debug = False):
    entity.d["SDB_NRECS"] = hex(rom[addr + 4] << 8 | \
                              rom[addr + 5] << 0)
    #if debug: print "Number of Records: %d" % entity.d["SDB_NRECS"]
    entity.d["SDB_VERSION"] = rom[addr + 6]
    if rom[addr + 7] == 0:
        entity.d["SDB_BUS_TYPE"] = "wishbone"
    elif rom[addr + 7] == 1:
        entity.d["SDB_BUS_TYPE"] = "storage"
    _parse_rom_component_element(entity, rom, addr, debug)
    if rom[addr + 63] != 0x00:
        raise SDBError("Interconnect element record does not match type: 0x%02X" % rom[addr + 63])

def _parse_rom_component_element(entity, rom, addr, debug = False):
    entity.d["SDB_START_ADDRESS"] =   hex(_convert_rom_to_int(rom[addr +  8: addr + 16]))
    entity.d["SDB_LAST_ADDRESS"] =    hex(_convert_rom_to_int(rom[addr + 16: addr + 24]))
    start_address = long(entity.d["SDB_START_ADDRESS"], 16)
    end_address = long(entity.d["SDB_LAST_ADDRESS"], 16)
    entity.set_size(end_address - start_address)
    _parse_rom_product_element(entity, rom, addr, debug)

def _parse_rom_product_element(entity, rom, addr, debug = False):
    entity.d["SDB_VENDOR_ID"] =       hex(_convert_rom_to_int(rom[addr + 24: addr + 32]))
    entity.d["SDB_DEVICE_ID"] =       hex(_convert_rom_to_int(rom[addr + 32: addr + 36]))
    core_version    =                 _convert_rom_to_int(rom[addr + 36: addr + 40])
    core_version_string =             "%1d" % ((core_version >> 24) & 0x0F)
    core_version_string +=            "."
    core_version_string +=            "%1d" % ((core_version >> 16) & 0x0F)
    core_version_string +=            "."
    core_version_string +=            "%02d" % ((core_version) & 0xFF)
    entity.d["SDB_CORE_VERSION"] =    core_version_string
    date =                            _convert_rom_to_int(rom[addr + 40: addr + 44])
    entity.d["SDB_DATE"] =            "%02d%02d/%02d/%02d" % (  date >> 24 & 0xFF,
                                                                date >> 16 & 0xFF,
                                                                date >> 8 & 0xFF,
                                                                date & 0xFF)
    #print "Date: %s" % entity.d["SDB_DATE"]
    entity.d["SDB_NAME"] =            rom[addr + 44:addr + 63].tostring().strip("\0")

def _parse_synthesis_element(entity, rom, addr, debug = False):
    entity.d["SDB_SYNTH_NAME"] =      rom[addr + 0x00:addr + 0x10].tostring().strip("\0")
    entity.d["SDB_SYNTH_COMMIT_ID"] = rom[addr + 0x10:addr + 0x20].tostring().strip("\0")
    entity.d["SDB_SYNTH_TOOL_NAME"] = rom[addr + 0x20:addr + 0x28].tostring().strip("\0")
    entity.d["SDB_SYNTH_TOOL_VER"] =  rom[addr + 0x28:addr + 0x2C].tostring()
    date =                            _convert_rom_to_int(rom[addr + 0x2C: addr + 0x30])
    entity.d["SDB_DATE"] =            "%02d%02d/%02d/%02d" % (  date >> 24 & 0xFF,
                                                                date >> 16 & 0xFF,
                                                                date >> 8 & 0xFF,
                                                                date & 0xFF)

    #entity.d["SDB_DATE"]       =      rom[addr + 40:addr + 48].tostring()
    entity.d["SDB_SYNTH_USER_NAME"] = rom[addr + 0x30:addr + 0x3F].tostring().strip("\0")

def _convert_rom_to_int(rom):
    s = ""
    val = 0
    for i in range(len(rom)):
        val = val << 8 | rom[i]
        #print "val: 0x%016X" % val

    return val


