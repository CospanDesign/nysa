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
import copy

#Project Modules
import utils
import verilog_utils as vutils
from verilog_utils import get_eol
import ibuilder_error

class ModuleBuilderError(ibuilder_error.IBuilderError):
    pass

def dict_to_signal(name, d):
    if d["size"] == 1:
        return name
    return "%s[%d:%d]" % (name, d["max_val"], d["min_val"])

def generate_module_ports(module_name,
                          port_dict,
                          param_dict = {},
                          debug = False):
    """
    Generates the name, parameters and port declarations of a verilog module

    Args:
        module_name (string): Name of the module to instantiate
        port_dict (dictionary): Port dictionary
            Format of port_dict:
                {
                    "input":{
                        "clk":{
                            "size":1
                        },
                        "rst":{
                            "size":1
                        },
                        "stimulus":{
                            "size":1
                        },
                        "array":{
                            "size":1
                            "max_val":31,
                            "min_val":0
                        },
                        "button":{
                            "size":1
                            "max_val":3,
                            "min_val":0
                        }
                    },
                    "output":{
                        "out1":{
                            "size":1
                        },
                        "led":{
                            "size":1
                            "max_val":3,
                            "min_val":0
                        }
                    },
                    "inout":{
                        "inout_test":{
                            "size":1
                        },
                        "inout":{
                            "size":1
                            "max_val":5,
                            "min_val":1
                        }
                    }
                }
            param_dict (dictionay): Parameter dictionary
                Format of param_dict
                {
                    "PARAMETER1":"1",
                    "PARAMETER2":"4"
                }
    Returns:
        (string): buffer instantiation

    Raises:
        ModuleBuilderError:
            -module_name is not a string
            -param dictionary incorrectly formatted
            -port dictionary incorrectly formatted
    """
    if not isinstance(module_name, str):
        raise ModuleBuilderError("module_builder: module_name is not a string")
    buf = ""

    if len(param_dict.keys()) > 0:
        num_params = len(param_dict.keys())
        param_count = 1

        buf = "module %s #(\n" % module_name
        for param in param_dict:
            buf += "\t{0:10}{1:12}{2:10}{3}{4}\n".format("parameter",
                                                         param,
                                                         "=",
                                                         param_dict[param],
                                                         get_eol(num_params,
                                                                      param_count))
            param_count += 1

        buf += ")(\n"
    else:
        buf = "module %s(\n" % module_name

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
        buf += "\t{0:22}{1}{2}\n".format("input", "clk", get_eol(num_ports, port_count))
        port_count += 1

    if "rst" in input_ports:
        buf += "\t{0:22}{1}{2}\n".format("input", "rst", get_eol(num_ports, port_count))
        port_count += 1

    if port_count != len(input_ports):
        buf += "\n"
        buf += "\t//inputs\n"

    for port in input_ports:
        if port == "clk":
            continue
        if port == "rst":
            continue

        port_sig = dict_to_signal(port, port_dict["input"][port])

        if "[" in port_sig and ":" in port_sig:
            port_name = "\t{0:10}[{1:11}{2}{3}\n".format(
                                                 "input",
                                                 port_sig.partition("[")[2],
                                                 port_sig.partition("[")[0],
                                                 get_eol(num_ports,
                                                              port_count))
            port_count += 1
        else:
            port_name = "\t{0:22}{1}{2}\n".format("input",
                                                port_sig,
                                                get_eol(num_ports,
                                                             port_count))
            port_count += 1
        buf += port_name

    if len(output_ports) > 0:
        buf += "\n"
        buf += "\t//outputs\n"
    for port in output_ports:
        port_sig = dict_to_signal(port, port_dict["output"][port])
        if "[" in port_sig and ":" in port_sig:
            port_name = "\t{0:10}[{1:11}{2}{3}\n".format(
                                                 "output",
                                                 port_sig.partition("[")[2],
                                                 port_sig.partition("[")[0],
                                                 get_eol(num_ports,
                                                              port_count))
            port_count += 1
        else:
            port_name = "\t{0:22}{1}{2}\n".format("output",
                                                port_sig,
                                                get_eol(num_ports,
                                                             port_count))
            port_count += 1
        buf += port_name

    if len(inout_ports) > 0:
        buf += "\n"
        buf += "\t//inouts\n"

    for port in inout_ports:
        port_sig = dict_to_signal(port, port_dict["inout"][port])
        if "[" in port_sig and ":" in port_sig:
            port_name = "\t{0:10}[{1:11}{2}{3}\n".format(
                                                 "inout",
                                                 port_sig.partition("[")[2],
                                                 port_sig.partition("[")[0],
                                                 get_eol(num_ports,
                                                              port_count))
            port_count += 1
        else:
            port_name = "\t{0:22}{1}{2}\n".format("inout",
                                                port_sig,
                                                get_eol(num_ports,
                                                             port_count))
            port_count += 1

        buf += port_name

    buf += ");\n"
    return string.expandtabs(buf, 2)

def generate_defines_buf(defines_dict):
    """
    XXX: This function is not ready to be used, the defines need to be organized (DO NOT USE)
    Generate a buffer with the specified defines

    Args:
        defines_dict (dictionary): list of define values in the format:
            'name':'value'

    Returns:
        (string): buffer with the defines specified

    Raises:
        Nothing
    """
    if len(defines_dict) == 0:
        return ""


    buf =  "\n"
    for define in defines_dict:
        buf += "`define %s %s\n" % (define, defines_dict[define])
    buf += "\n"
    return buf

def generate_timespec_buf(step = "1 ns", unit = "1 ps"):
    """
    Generate a timespec buffer given the input, if left empty fills in the
    default of 1ns/1ps

    Args:
        step (string): Timespec step
        unit (string): Unit of time step

    Returns:
        (string): buffer with the given timespec

    Raises:
        Nothing
    """
    buf  = "\n"
    buf += "`timescale %s/%s\n" % (step, unit)
    buf += "\n"
    return buf


class ModuleBuilder(object):
    """Class used to build a generic verilog module given a configuratiom file"""

    def __init__(self, tags = None):
        self.tags = tags
        self.wires = {}
        self.bindings = {}
        self.user_paths = []
        self.submodule_buffers = []

       
    def add_ports_to_wires(self):
        """Add all input and output wires to the ports"""

        if "input" in self.tags["ports"]:
            for port in self.tags["ports"]["input"]:
                #print "Adding %s to wires" % port
                self.wires[port] = self.tags["ports"]["input"][port]
        if "output" in self.tags["ports"]:
            for port in self.tags["ports"]["output"]:
                self.wires[port] = self.tags["ports"]["output"][port]

    def generate_module_wires(self, invert_reset):
        buf = ""
        buf += vutils.create_wire_buf("rst_n", 1, 0, 0)
        return buf

    def generate_module(self, name, tags = None, invert_reset = False, debug = False):
        self.wires = {}
        self.bindings = {}
        self.submodule_buffers = []
        if tags:
            self.tags = tags

        #Add the ports to wires
        self.add_ports_to_wires()

        #Generate the submodules
        if "submodules" in self.tags:
            for submodule in self.tags["submodules"]:
                sub = self.generate_sub_module(invert_reset,
                                               submodule,
                                               self.tags["submodules"][submodule],
                                               debug = False)

                self.submodule_buffers.append(sub)

        #Generate the bindings or assignments for the submodules
        assign_buf = vutils.generate_assigns_buffer(invert_reset,
                                                    bindings = self.bindings,
                                                    internal_bindings = {},
                                                    debug = False)

        wire_buf = self.generate_module_wires(invert_reset)

        buf =  generate_timespec_buf()
        buf = ""
        param_dict = {}
        if "parameters" in self.tags:
            param_dict = self.tags["parameters"]

        buf += generate_module_ports(module_name = name,
                                     port_dict = self.tags["ports"],
                                     param_dict = param_dict,
                                     debug = False)

        buf += "\n"
        buf += "//local parameters\n"
        buf += "\n"
        buf += "//registers/wires\n"
        buf += wire_buf
        buf += "\n"
        buf += "//submodules\n"
        buf += "\n"


        for sub in self.submodule_buffers:
            buf += sub
            buf += "\n"

        buf += "\n"
        buf += assign_buf
        buf += "//asynchronous logic\n"
        buf += "//synchronous logic\n"
        buf += "\n"
        buf += "endmodule"
        return buf
        

    def generate_sub_module_wires(self, invert_reset, instance_name, module_tags):
        #Add all input and output wires to the ports
        buf = ""
        if "input" in module_tags["ports"]:
            buf += "//inputs\n"
            for port in module_tags["ports"]["input"]:
                if port == "clk":
                    continue
                if port == "rst":
                    continue
                pname = port
                if len(instance_name) > 0:
                    pname = "%s_%s" % (instance_name, port)

                if self.in_wires(pname, module_tags["ports"]["input"][port]):
                    continue

                buf += vutils.create_wire_buf_from_dict(pname,
                                                        module_tags["ports"]["input"][port])
                self.add_wire(pname, module_tags["ports"]["input"][port])

            buf += "\n"

        if "output" in module_tags["ports"]:
            buf += "//outputs\n"
            for port in module_tags["ports"]["output"]:
                pname = port
                if len(instance_name) > 0:
                    pname = "%s_%s" % (instance_name, port)

                if self.in_wires(pname, module_tags["ports"]["output"][port]):
                    continue

                buf += vutils.create_wire_buf_from_dict(pname,
                                                        module_tags["ports"]["output"][port])

                self.add_wire(pname, module_tags["ports"]["output"][port])
            buf += "\n"

        return buf

    def generate_sub_module(self,
                            invert_reset,
                            instance_name,
                            config_tags,
                            module_tags = None,
                            enable_unique_ports = True,
                            debug = False):


        if module_tags is None:
            filepath = utils.find_rtl_file_location(config_tags["filename"],
                                                    self.user_paths)
            module_tags = vutils.get_module_tags(filepath,
                                                user_paths = self.user_paths)
        #if debug:
            #print "Module Tags:"
            #utils.pretty_print_dict(module_tags)

        buf =  "//Module %s (  %s  )\n" % (module_tags["module"], instance_name)
        buf += "\n"
        prename = ""
        if enable_unique_ports:
            prename = instance_name
        buf += self.generate_sub_module_wires(invert_reset, prename, module_tags)


        buf += vutils.generate_module_port_signals(invert_reset = invert_reset,
                                                   name = instance_name,
                                                   prename = prename,
                                                   slave_tags = config_tags,
                                                   module_tags = module_tags)

        #Add the bindings for this modules to the bind dictionary
        if "bind" in config_tags:
            for bind in config_tags["bind"]:
                bname = bind
                if len(prename) > 0:
                    bname = "%s_%s" % (prename, bind)
                self.bindings[bname] = {}
                self.bindings[bname] = config_tags["bind"][bind]

        return buf

    def in_wires(self, signal_name, signal_dict):
        if signal_name not in self.wires.keys():
            return False
        wire_dict = self.wires[signal_name]
        if signal_dict["size"] == wire_dict["size"]:
            return True

        if signal_dict["size"] < wire_dict["size"]:
            return True
        return False

    def add_wire(self, signal_name, signal_dict):
        if signal_name not in self.wires.keys():
            self.wires[signal_name] = signal_dict
            return

