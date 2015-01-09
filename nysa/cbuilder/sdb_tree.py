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
    
    def __init__(self):
        self.informative_list = []
        self.unsorted_devices = []
        self.bus = collections.OrderedDict()

    def reset_tree(self):
        self.informative_list = []
        self.unsorted_devices = []
        self.bus = collections.OrderedDict()

    def insert_interconnect(self, interconnect):
        #Analyze the address range of the interconnect

        #Go through any of the unsorted devices to determine if they belong in this bus

        #Go through all of the interconnects to determine if a device should be pulled from a higher
        #interconnect and brought down to this lower one
        pass


    def insert_device(self, device):
        #Analyze the start address of the device
        #XXX: It is assumed that a device should start and end within a bus so I only need to look at the start

        #If this device was inserted before a host interconnect was found
        #Then put it in the unsorted devices list
        pass

    def insert_bridge(self, bridge):
        pass

    def insert_integration_record(self, interconnect, integration):
        self.informative_list.append(integration)

    def insert_url(self, url):
        self.informative_list.append(url)

    def insert_sythesis_record(self, synthesis_record):
        self.informative_list.append(synthesis_record)

