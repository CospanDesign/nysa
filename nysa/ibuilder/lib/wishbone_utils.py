# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (http://ninja-ide.org).
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

"""Utilities used in detecting and generating wishbone cores
   and generating top.v files for images
"""

"""
Log:
06/25/2013
    -Initial Commit
09/10/2013
    -Adding WishboneTopGenerator
    -Changed License to GPL V3
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import re
from string import Template

PATH_TO_TOP = os.path.abspath(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              "cbuilder",
                              "template",
                              "top",
                              "top.v"))


#Nysa imports


def is_wishbone_bus_signal(signal):
    #Look for a wishbone slave signal
    if re.search("i_wbs_we", signal) is not None:
        return True
    if re.search("i_wbs_stb", signal) is not None:
        return True
    if re.search("i_wbs_cyc", signal) is not None:
        return True
    if re.search("i_wbs_sel", signal) is not None:
        return True
    if re.search("i_wbs_adr", signal) is not None:
        return True
    if re.search("i_wbs_dat", signal) is not None:
        return True
    if re.search("o_wbs_dat", signal) is not None:
        return True
    if re.search("o_wbs_ack", signal) is not None:
        return True
    if re.search("o_wbs_int", signal) is not None:
        return True

    #Look for a wishbone master signal
    if re.search("o_.*_we$", signal) is not None:
        return True
    if re.search("o_.*_stb$", signal) is not None:
        return True
    if re.search("o_.*_cyc$", signal) is not None:
        return True
    if re.search("o_.*_sel$", signal) is not None:
        return True
    if re.search("o_.*_adr$", signal) is not None:
        return True
    if re.search("o_.*_dat$", signal) is not None:
        return True
    if re.search("i_.*_dat$", signal) is not None:
        return True
    if re.search("i_.*_ack$", signal) is not None:
        return True
    if re.search("i_.*_int$", signal) is not None:
        return True
    return False


class WishboneTopGenerator(object):
    def __init__(self):
        f = open(PATH_TO_TOP, "r")
        self.buf = f.read()
        self.port_buf = ""
        self.arb_buf = ""
        self.wr_buf = ""
        self.wi_buf = ""
        self.wmi_buf = ""
        self.wm_buf = ""

    def generate_top(self):
        pass

    def generate_sim_top(self):
        pass

    def generate_ports(self):
        pass

    def add_ports_to_wires(self):
        pass

    def generate_wishbone_peripheral_slave(self,
                                name = "",
                                index = -1,
                                module_tags = {},
                                debug = False):
        pass

                                
    def generate_wishbone_memory_slave(self,
                                name = "",
                                index = -1,
                                module_tags = {},
                                debug = False):
        pass

    def generate_host_interface_buffer(self,
                                debug = False):
        pass

    def generate_wishbone_buffer(self,
                                 name="",
                                 index=-1,
                                 module_tags = {},
                                 mem_slave=False,
                                 io_module=False,
                                 debug=False):
        pass

    def generate_arbitor_buffer(self, debug = False):
        pass

    def generate_parameters(self, name="", module_tags={}, debug = False):
        pass

    def generate_assigns(self, debug=False):
        pass
