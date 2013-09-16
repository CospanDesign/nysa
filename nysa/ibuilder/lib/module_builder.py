# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa.
#
#       (http://wiki.cospandesign.com/index.php?title=Nysa.org)
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

"""module_builder

Use configuration files to generate verilog modules
"""

"""
Changes:
9/16/2013:
    -Initial Commit
"""


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import string
import json

#Project Modules
import utils
import verilog_utils as vutils
import ibuilder_error

class ModuleBuilderError(ibuilder_error.IBuilderError):
    pass

def get_port_eol(num_ports, index):
    if index < num_ports:
        return ","
    return ""

def generate_module_ports(module_name, port_dict, debug = False):
    buf =  "module %s(\n" % module_name

    input_ports  =[]
    output_ports = []
    inout_ports = []

    port_count = 0

    if "input" in port_dict:
        for port in port_dict["input"]:
            input_ports.append(port)

    if "output" in port_dict:
        for port in port_dict["output"]:
            output_ports.append(port)

    if "inout" in port_dict:
        for port in port_dict["inout"]:
            inout_ports.append(port)

    #Sort the signals
    input_ports = sorted(input_ports, cmp = vutils.port_cmp)
    output_ports = sorted(output_ports, cmp = vutils.port_cmp)
    inout_ports = sorted(inout_ports, cmp = vutils.port_cmp)

    num_ports = len(input_ports) + len(output_ports) + len(inout_ports)
    port_count = 1
    port_name = ""

    if debug:
        print "input ports: %s" % str(input_ports)

    #This is a special case which should not handle an array
    if "clk" in input_ports:
        buf += "\t{0:20}\t{1}{2}\n".format("input", "clk", get_port_eol(num_ports, port_count))
        port_count += 1

    if "rst" in input_ports:
        buf += "\t{0:20}\t{1}{2}\n".format("input", "rst", get_port_eol(num_ports, port_count))
        port_count += 1

    if port_count != len(input_ports):
        buf += "\n"
        buf += "\t//inputs\n"

    for port in input_ports:
        if port == "clk":
            continue
        if port == "rst":
            continue

        if "[" in port and ":" in port:
            print "Found an array in the input ports: %s" % port
            port_name = "\t{0:10}[{1:11}{2}{3}\n".format(
                                                 "input",
                                                 port.partition("[")[2], 
                                                 port.partition("[")[0], 
                                                 get_port_eol(num_ports,
                                                              port_count))
            port_count += 1
        else:
            port_name = "\t{0:22}{1}{2}\n".format("input",
                                                port,
                                                get_port_eol(num_ports,
                                                             port_count))
            port_count += 1
        buf += port_name

    if len(output_ports) > 0:
        buf += "\n"
        buf += "\t//outputs\n"
    for port in output_ports:
        if "[" in port and ":" in port:
            port_name = "\t{0:10}[{1:11}{2}{3}\n".format(
                                                 "output",
                                                 port.partition("[")[2], 
                                                 port.partition("[")[0], 
                                                 get_port_eol(num_ports,
                                                              port_count))
            port_count += 1
        else:
            port_name = "\t{0:22}{1}{2}\n".format("output",
                                                port,
                                                get_port_eol(num_ports,
                                                             port_count))
            port_count += 1
        buf += port_name

    if len(inout_ports) > 0:
        buf += "\n"
        buf += "\t//inouts\n"

    for port in inout_ports:
        if "[" in port and ":" in port:
            port_name = "\t{0:10}[{1:11}{2}{3}\n".format(
                                                 "inout",
                                                 port.partition("[")[2], 
                                                 port.partition("[")[0], 
                                                 get_port_eol(num_ports,
                                                              port_count))
            port_count += 1
        else:
            port_name = "\t{0:22}{1}{2}\n".format("inout",
                                                port,
                                                get_port_eol(num_ports,
                                                             port_count))
            port_count += 1

        buf += port_name

    buf += ");\n"
    return string.expandtabs(buf, 2)

