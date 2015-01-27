# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (wiki.cospandesign.com/index.php?title=Nysa).
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


# -*- coding: utf-8 -*-


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

from common.status import Status

from cbuilder.sdb_component  import SDB_ROM_RECORD_LENGTH
from cbuilder import sdb_component as sdbc
from cbuilder import sdb_object_model as som
from cbuilder import som_rom_parser as srp
from cbuilder.sdb import SDBError

class NysaSDBManager(object):

    def __init__(self, status = None):
        self.s = status
        if self.s is None:
            self.s = Status()

    def is_memory_device(self, device_index):
        pass

    def is_wishbone_bus(self):
        pass

    def is_axie_bus(self):
        pass

    def get_number_of_devices(self):
        pass

    def find_device(self, vendor_id, product_id):
        pass

    def get_address_from_index(self, device_index):
        pass

    def get_product_id_from_index(self, device_index):
        pass

    def get_size_from_index(self, device_index):
        pass

    def get_board_name(self):
        pass

    def pretty_print_sdb(self):
        print "Pretty pring SDB"
        pass

    def get_total_memory_size(self):
        pass

    def read_sdb(self, n):
        self.s.Verbose("Parsing Top Interconnect Buffer")
        #Because Nysa works with many different platforms we need to get the
        #platform specific location of where the SDB actually is
        #XXX: Create this function in nysa
        sdb_base_address = n.get_sdb_base_address()
        self.som = som.SOM()
        self.som.initialize_root()
        bus = self.som.get_root()
        _parse_bus(n, self.som, bus, sdb_base_address, sdb_base_address, self.s)


def _parse_bus(n, som, bus, addr, base_addr, status):
    #The first element at this address is the interconnect
    status.Verbose("Bus @ 0x%08X" % addr)
    entity_rom = n.read(addr, SDB_ROM_RECORD_LENGTH / 4)
    print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
    bus_entity = srp.parse_rom_element(entity_rom)
    if not bus_entity.is_interconnect():
        raise SDBError("Rom data does not point to an interconnect")
    num_devices = bus_entity.get_number_of_records_as_int()
    status.Verbose("\tFound %d Devices" % num_devices)
    som.set_bus_component(bus, bus_entity)
    print "Found bus: %s" % bus_entity.get_name()

    entity_size = []
    entity_addr_start = []

    for i in range(1, (num_devices + 1)):
        I = (i * (SDB_ROM_RECORD_LENGTH / 4)) + addr
        entity_rom = n.read(I, SDB_ROM_RECORD_LENGTH / 4)
        print_sdb_rom(sdbc.convert_rom_to_32bit_buffer(entity_rom))
        entity = srp.parse_rom_element(entity_rom)
        end = long(entity.get_end_address_as_int())
        start = long(entity.get_start_address_as_int())
        entity_addr_start.append(start)
        entity_size.append(end - start)

        if entity.is_bridge():
            print "Found bridge"
            sub_bus = som.insert_bus(root = bus,
                                     name = entity.get_name())
            sub_bus_addr = entity.get_bridge_address_as_int() * 2 + base_addr
            print "address: 0x%08X" % sub_bus_addr
            _parse_bus(n, som, sub_bus, sub_bus_addr, base_addr, status)
        else:
            som.insert_component(root = bus, component = entity)

    #Calculate Spacing
    spacing = 0
    prev_start = None
    prev_size = None
    for i in range (num_devices):
        size = entity_size[i]
        start_addr = entity_addr_start[i]
        if prev_start is None:
            prev_size = size
            prev_start = start_addr
            continue

        potential_spacing = (start_addr - prev_start)
        if potential_spacing > prev_size:
            if potential_spacing > 0 and spacing == 0:
                spacing = potential_spacing
            if spacing > potential_spacing:
                spacing = potential_spacing

        prev_size = size
        prev_start = start_addr

    som.set_child_spacing(bus, spacing)



    
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


