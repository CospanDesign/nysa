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


from PyQt4.Qt import *
from PyQt4.QtCore import *

from status import Status
from actions import Actions

from nplatform.nplatform import Platform

class PlatformScanner(QObject):
    def __init__(self):
        super(PlatformScanner, self).__init__()
        self.status = Status()
        self.n = None
        self.uid = None
        self.dev_type = None

    def refresh_platforms(self):
        plat_dir = os.path.join(os.path.dirname(__file__), "nplatform")
        plat_files = os.listdir(plat_dir)
        plat_classes = []
        for f in plat_files:
            #Removed compiled python modules from the list
            if f.endswith("pyc"):
                continue

            #Remove package modules
            if f.startswith("__init__"):
                continue

            f = f.split(".")[0]
            m = __import__("nplatform.%s" % f)
            for name in dir(m):
                item = getattr(m, name)
                if not ismodule(item):
                    continue
                
                for mname in dir(item):
                    #print "Name: %s" % mname
                    #print "Type: %s" % str(type(mname))
                    obj = getattr(item, mname)

                    if not isclass(obj):
                        continue
                    if issubclass(obj, Platform) and obj is not Platform:
                        unique = True
                        for plat_class in plat_classes:
                            if str(plat_class) == str(obj):
                                unique = False
                        if unique:
                            #print "Adding Class: %s" % str(obj)
                            plat_classes.append(obj)

        plat_instances = []
        for pc in plat_classes:
            plat_instances.append(pc())

        plat_dict = {}
        for pi in plat_instances:
            plat_dict[pi.get_type()] = pi.scan()

        print "Plat Dict: %s" % str(plat_dict)
        return plat_dict


def drt_to_config(n):

    config_dict = {}

    #Read the board id and find out what type of board this is
    config_dict["board"] = n.get_board_name()
    print "Name: %s" % config_dict["board"]

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

