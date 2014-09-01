# Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

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


""" nysa platform scanner
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
from inspect import isclass
from inspect import ismodule

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from common.site_manager import SiteManager
from platform import Platform

class PlatformScanner(object):
    def __init__(self, status = None):
        super(PlatformScanner, self).__init__()
        self.s = status
        self.n = None
        self.uid = None
        self.dev_type = None

    def get_board_path_dict(self):
        sm = SiteManager()
        board_names = sm.get_local_board_names()
        board_path_dict = {}
        for bname in board_names:
            board_path_dict[bname] = sm.get_board_directory(bname)
        return board_path_dict

    def get_platforms(self):
        board_path_dict = self.get_board_path_dict()

        #platform_paths_list = []
        module_dict = {}

        plat_class_dict = {}
        for board in board_path_dict:
            platform_paths_list = os.path.join(board_path_dict[board], board)
            sys.path.append(os.path.join(board_path_dict[board]))

            m = __import__("%s.platform" % board)
            board_platform = m.platform

            for name in dir(board_platform):

                item = getattr(board_platform, name)
                if not isclass(item):
                    continue

                #XXX: Kinda Jenkie
                if "IS_PLATFORM" in dir(item) and item.__name__ is not "Platform":
                    if self.s: self.s.Debug("Found: %s" % name)
                    unique = True
                    for plat_class in plat_class_dict:
                        if str(plat_class) == str(item):
                            unique = False
                    if unique:
                        #print "Adding Class: %s" % str(item)
                        plat_class_dict[board] = item

            if self.s: self.s.Debug("Platform Classes: %s" % str(plat_class_dict))

        return plat_class_dict


def drt_to_config(n):

    config_dict = {}
    print "Pretty print:"
    n.pretty_print_drt()

    #Read the board id and find out what type of board this is
    config_dict["board"] = n.get_board_name()
    #print "Name: %s" % config_dict["board"]

    #Read the bus flag (Wishbone or Axie)
    if n.is_wishbone_bus():
        config_dict["bus_type"] = "wishbone"
        config_dict["TEMPLATE"] = "wishbone_template.json"
    if n.is_axie_bus():
        config_dict["bus_type"] = "axie"
        config_dict["TEMPLATE"] = "axie_template.json"

    config_dict["SLAVES"] = {}
    config_dict["MEMORY"] = {}
    #Read the number of slaves
    #Go thrugh each of the slave devices and find out what type it is
    for i in range (n.get_number_of_devices()):
        if n.is_memory_device(i):
            name = "Memory %d" % i
            config_dict["MEMORY"][name] = {}
            config_dict["MEMORY"][name]["sub_id"] = n.get_device_sub_id(i)
            config_dict["MEMORY"][name]["unique_id"] = n.get_device_unique_id(i)
            config_dict["MEMORY"][name]["address"] = n.get_device_address(i)
            config_dict["MEMORY"][name]["size"] = n.get_device_size(i)
            continue

        name = n.get_device_name_from_id(n.get_device_id(i))
        config_dict["SLAVES"][name] = {}
        #print "Name: %s" % n.get_device_name_from_id(n.get_device_id(i))
        config_dict["SLAVES"][name]["id"] = n.get_device_id(i)
        config_dict["SLAVES"][name]["sub_id"] = n.get_device_sub_id(i)
        config_dict["SLAVES"][name]["unique_id"] = n.get_device_unique_id(i)
        config_dict["SLAVES"][name]["address"] = n.get_device_address(i)
        config_dict["SLAVES"][name]["size"] = n.get_device_size(i)

    config_dict["INTERFACE"] = {}
    return config_dict
    #Read the number of memory devices

