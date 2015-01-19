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

from sdb import SDB
from sdb import SDBInfo
from sdb import SDBError
import collections

class SDBTree(object):

    def __init__(self, status):
        self.informative_list = []
        self.bus = collections.OrderedDict()
        self.s = status
        self.current_element = None

    def reset_tree(self):
        self.informative_list = []
        self.bus = collections.OrderedDict()
        self.current_element = None

    def insert_top_interconnect(self, interconnect):
        name = interconnect.d["SDB_NAME"]
        self.bus[name] = [interconnect, []]
        self.current_element = self.bus[name]

    def insert_interconnect(self, interconnect):
        #Analyze the address range of the interconnect

        #Go through any of the unsorted devices to determine if they belong in this bus

        #Go through all of the interconnects to determine if a device should be pulled from a higher
        #interconnect and brought down to this lower one
        pass

    def insert_device(self, device):
        device_list = self.current_element[1]
        if len(device_list) == 0:
            device_list.append(device):
            return

        if device.get_start_address_as_int() == 0x00:
            device_list.insert(0, device)
            return

        #Analyze the start address of the device
        start_addr = 0
        for i in range(len(device_list)):
            curr_dev_addr = device_list[i].get_start_address_as_int()
            dev_addr = device.get_start_address_as_int()
            #If device at pos start addr < device start address, continue
            if curr_dev_addr < dev_addr:
                continue
            else:
                device_list.insert(i, device)
                return

        device_list.append(device)

    def insert_bridge(self, bridge):
        pass

    def insert_integration_record(self, interconnect, integration):
        self.informative_list.append(integration)

    def insert_url(self, url):
        self.informative_list.append(url)

    def insert_sythesis_record(self, synthesis_record):
        self.informative_list.append(synthesis_record)

