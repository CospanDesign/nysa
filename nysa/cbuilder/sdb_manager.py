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

import sdb
import sdb_rom
from sdb_tree import SDBTree

from nysa.common.status import Status

from nysa.common.status import white
from nysa.common.status import gray
from nysa.common.status import red
from nysa.common.status import green
from nysa.common.status import yellow
from nysa.common.status import blue
from nysa.common.status import purple
from nysa.common.status import cyan

class SDBManager(object):

    def __init__(self, status = None):
        self.s = status
        if self.s is None:
            self.s = Status()
        self.sdb_tree = SDBTree(self.s)

    def parse_top_interconnect_buffer(self, buf):
        self.s.Verbose("Parsing Top Interconnect Buffer")
        self.s.Verbose("Buffer: %s" % str(buf))
        s = sdb.SDB()
        element = s.parse_rom_element(buf)
        self.sdb_tree.reset_tree()
        self.sdb_tree.insert_top_interconnect(element)

    def set_sdb(self, sdb_rom):
        pass

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
        pass

    def get_total_memory_size(self):
        pass


