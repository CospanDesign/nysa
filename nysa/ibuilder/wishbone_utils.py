# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# This file is part of Nysa (http://wiki.cospandesign.com/index.php?title=Nysa).
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
import copy
import string
from string import Template

PATH_TO_TOP = os.path.abspath(os.path.join(os.path.dirname(__file__),
                              os.pardir,
                              "data",
                              "template",
                              "top",
                              "top.v"))

#Nysa imports
import utils
import verilog_utils as vutils
import arbiter

IF_WIRES = [
    "ingress_clk",
    "ingress_rdy",
    "ingress_act",
    "ingress_stb",
    "ingress_data",
    "ingress_size",
    "egress_clk",
    "egress_rdy",
    "egress_act",
    "egress_stb",
    "egress_data",
    "egress_size",
    "sync_rst"
]

IO_TYPES = [
    "input",
    "output",
    "inout"
]

def is_wishbone_slave_signal(signal):
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
    return False



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

def generate_defines(define_dict):
    buf = "//Defines\n"
    for key in define_dict:
        buf += "`define %s" % key
        if len(define_dict[key]) > 0:
            buf += " %s" % define_dict[key]
        buf += "\n"

    buf += "\n"
    return buf


def generate_startup():
    buf = "//Startup reset\n\n"
    buf +=create_wire_buf("startup_rst", 1, 0, 0)
    buf += "\n"
    buf += "startup start(\n"
    buf += "\t.{0:20}({1:20}),\n".format("clk", "clk")
    buf += "\t.{0:20}({1:20})\n".format("startup_rst", "startup_rst")
    buf += ");\n"
    return string.expandtabs(buf, 2)

def generate_peripheral_wishbone_interconnect_buffer(num_slaves, invert_reset):
    buf = "//Wishbone Memory Interconnect\n\n"
    buf += "wishbone_interconnect wi (\n"
    buf += "\t.{0:20}({1:20}),\n".format("clk", "clk")
    if invert_reset:
        buf += "\t.{0:20}({1:20}),\n".format("rst", "rst_n | startup_rst")
    else:
        buf += "\t.{0:20}({1:20}),\n".format("rst", "rst | startup_rst")
    buf += "\n"

    buf += "\t//master\n"
    buf += "\t.{0:20}({1:20}),\n".format("i_m_we",  "wbm_we_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_cyc", "wbm_cyc_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_stb", "wbm_stb_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_sel", "wbm_sel_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_m_ack", "wbm_ack_i")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_dat", "wbm_dat_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_m_dat", "wbm_dat_i")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_adr", "wbm_adr_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_m_int", "wbm_int_i")
    buf += "\n"

    for i in range (0, num_slaves):
        buf += "\t//slave %d\n" % i
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_we" % i,  "s%d_i_wbs_we" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_cyc" % i, "s%d_i_wbs_cyc" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_stb" % i, "s%d_i_wbs_stb" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_sel" % i, "s%d_i_wbs_sel" % i)
        buf += "\t.{0:20}({1:20}),\n".format("i_s%d_ack" % i, "s%d_o_wbs_ack" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_dat" % i, "s%d_i_wbs_dat" % i)
        buf += "\t.{0:20}({1:20}),\n".format("i_s%d_dat" % i, "s%d_o_wbs_dat" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_adr" % i, "s%d_i_wbs_adr" % i)
        buf += "\t.{0:20}({1:20})".format("i_s%d_int" % i, "s%d_o_wbs_int" % i)

        if (i < num_slaves - 1):
            buf += ",\n"

        buf += "\n"

    buf += ");"
    return string.expandtabs(buf, 2)


def generate_memory_wishbone_interconnect_buffer(num_mem_slaves, invert_reset):
    if num_mem_slaves == 0:
        return ""

    buf =  "//Wishbone Memory Interconnect\n\n"
    buf += "wishbone_mem_interconnect wmi (\n"
    buf += "\t.{0:20}({1:20}),\n".format("clk", "clk")
    if invert_reset:
        buf += "\t.{0:20}({1:20}),\n".format("rst", "rst_n | startup_rst")
    else:
        buf += "\t.{0:20}({1:20}),\n".format("rst", "rst | startup_rst")
    buf += "\n"

    buf += "\t//master\n"
    buf += "\t.{0:20}({1:20}),\n".format("i_m_we",  "mem_we_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_cyc", "mem_cyc_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_stb", "mem_stb_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_sel", "mem_sel_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_m_ack", "mem_ack_i")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_dat", "mem_dat_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_m_dat", "mem_dat_i")
    buf += "\t.{0:20}({1:20}),\n".format("i_m_adr", "mem_adr_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_m_int", "mem_int_i")
    buf += "\n\n"

    for i in range (num_mem_slaves):
        buf += "\t//slave %d\n" % i
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_we" % i,  "sm%d_i_wbs_we" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_cyc" % i, "sm%d_i_wbs_cyc" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_stb" % i, "sm%d_i_wbs_stb" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_sel" % i, "sm%d_i_wbs_sel" % i)
        buf += "\t.{0:20}({1:20}),\n".format("i_s%d_ack" % i, "sm%d_o_wbs_ack" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_dat" % i, "sm%d_i_wbs_dat" % i)
        buf += "\t.{0:20}({1:20}),\n".format("i_s%d_dat" % i, "sm%d_o_wbs_dat" % i)
        buf += "\t.{0:20}({1:20}),\n".format("o_s%d_adr" % i, "sm%d_i_wbs_adr" % i)
        buf += "\t.{0:20}({1:20})".format("i_s%d_int" % i, "sm%d_o_wbs_int" % i)

        if (i < num_mem_slaves - 1):
            buf += ",\n"

        buf += "\n"

    buf += ");"
    return string.expandtabs(buf, 2)

def generate_master_buffer(invert_reset):
    buf = "//Wishbone Master\n\n"
    buf += "wishbone_master wm (\n"
    buf += "\t.{0:20}({1:20}),\n".format("clk","clk")

    if invert_reset:
        buf += "\t.{0:20}({1:20}),\n\n".format("rst", "rst_n | startup_rst")
    else:
        buf += "\t.{0:20}({1:20}),\n\n".format("rst", "rst | startup_rst")

    buf += "\t//input handler signals\n"
    buf += "\t.{0:20}({1:20}),\n".format("i_ingress_clk", "ingress_clk")
    buf += "\t.{0:20}({1:20}),\n".format("o_ingress_rdy", "ingress_rdy")
    buf += "\t.{0:20}({1:20}),\n".format("i_ingress_act", "ingress_act")
    buf += "\t.{0:20}({1:20}),\n".format("i_ingress_stb", "ingress_stb")
    buf += "\t.{0:20}({1:20}),\n".format("i_ingress_data", "ingress_data")
    buf += "\t.{0:20}({1:20}),\n\n".format("o_ingress_size", "ingress_size")

    buf += "\t//output handler signals\n"
    buf += "\t.{0:20}({1:20}),\n".format("i_egress_clk", "egress_clk")
    buf += "\t.{0:20}({1:20}),\n".format("o_egress_rdy", "egress_rdy")
    buf += "\t.{0:20}({1:20}),\n".format("i_egress_act", "egress_act")
    buf += "\t.{0:20}({1:20}),\n".format("i_egress_stb", "egress_stb")
    buf += "\t.{0:20}({1:20}),\n".format("o_egress_data", "egress_data")
    buf += "\t.{0:20}({1:20}),\n\n".format("o_egress_size", "egress_size")

    buf += "\t.{0:20}({1:20}),\n\n".format("o_sync_rst", "mstr_rst")

    buf += "\t//interconnect signals\n"
    buf += "\t.{0:20}({1:20}),\n".format("o_per_we", "wbm_we_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_per_adr", "wbm_adr_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_per_dat", "wbm_dat_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_per_dat", "wbm_dat_i")
    buf += "\t.{0:20}({1:20}),\n".format("o_per_stb", "wbm_stb_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_per_cyc", "wbm_cyc_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_per_msk", "wbm_msk_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_per_sel", "wbm_sel_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_per_ack", "wbm_ack_i")
    buf += "\t.{0:20}({1:20}),\n\n".format("i_per_int", "wbm_int_i")

    buf += "\t//memory interconnect signals\n"
    buf += "\t.{0:20}({1:20}),\n".format("o_mem_we", "mem_we_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_mem_adr", "mem_adr_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_mem_dat", "mem_dat_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_mem_dat", "mem_dat_i")
    buf += "\t.{0:20}({1:20}),\n".format("o_mem_stb", "mem_stb_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_mem_cyc", "mem_cyc_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_mem_msk", "mem_msk_o")
    buf += "\t.{0:20}({1:20}),\n".format("o_mem_sel", "mem_sel_o")
    buf += "\t.{0:20}({1:20}),\n".format("i_mem_ack", "mem_ack_i")
    buf += "\t.{0:20}({1:20})\n\n".format("i_mem_int", "mem_int_i")
    buf += ");"
    return string.expandtabs(buf, 2)

def create_wire_buf(name, size, max_val, min_val):
    line = ""
    if size > 1:
        size_range = "[%d:%d]" % (max_val, min_val)
        line = "wire\t{0:15}{1};\n".format(size_range, name)
    else:
        line = "wire\t{0:15}{1};\n".format("", name)
    return string.expandtabs(line, 2)

def get_port_count(module_tags = {}):
    port_count = 0
    if "inout" in module_tags["ports"]:
        port_count += len(module_tags["ports"]["inout"])
    if "output" in module_tags["ports"]:
        port_count += len(module_tags["ports"]["output"])
    if "input" in module_tags["ports"]:
        port_count += len(module_tags["ports"]["input"])
    return port_count


def generate_module_port_signals(invert_reset,
                                 wishbone_prename = "",
                                 instance_name = "",
                                 slave_tags = {},
                                 module_tags = {},
                                 add_startup_rst = True,
                                 host_interface = False):


    debug = False
    buf = "(\n"
    #Add the port declarations
    buf += "\t.{0:<20}({1:<20}),\n".format("clk", "clk")
    reset_name = "rst"
    if invert_reset:
        reset_name = "rst_n"

    if add_startup_rst:
        reset_name += " | startup_rst"

    if not host_interface:
        reset_name += " | mstr_rst"

    buf += "\t.{0:<20}({1:<20}),\n".format("rst", reset_name)

    #Keep track of the port count so the last one won't have a comma
    port_max = get_port_count(module_tags)
    #print "instance name: %s" % instance_name
    #if instance_name == "wb_i2c_0":
    #    print "port max: %d" % port_max
    port_count = 0

    input_ports = []
    output_ports = []
    inout_ports = []
    if "input" in module_tags["ports"]:
        input_ports = module_tags["ports"]["input"].keys()
    if "output" in module_tags["ports"]:
        output_ports = module_tags["ports"]["output"].keys()
    if "inout" in module_tags["ports"]:
        inout_ports = module_tags["ports"]["inout"].keys()

    for port in input_ports:
        port_count += 1
        line = ""
        if port == "rst":
            continue
        if port == "clk":
            continue

        #Check to see if this is one of the pre-defined wires
        wire = ""
        for w in IF_WIRES:
            if w == port:
                wire = "%s" % w
                break

        #Not Pre-defines
        if len(wire) == 0:
            if is_wishbone_slave_signal(port):
                wire = "%s%s" % (wishbone_prename, port)
            else:
                if len(instance_name) > 0:
                    wire = "%s_%s" % (instance_name, port)
                else:
                    wire = "%s" % port

        line = "\t.{0:<20}({1:<20})".format(port, wire)
        if port_count == port_max:
            buf += "%s\n" % line
        else:
            buf += "%s,\n" % line


    for port in output_ports:
        port_count += 1
        if port == "rst":
            continue
        if port == "clk":
            continue

        line = ""
        #Check to see if this is one of the pre-defined wires
        wire = ""
        for w in IF_WIRES:
            if w == port:
                #wire = "%s" % w[2:]
                wire = "%s" % w
                break

        #Not Pre-defines
        if len(wire) == 0:
            if is_wishbone_slave_signal(port):
                wire = "%s%s" % (wishbone_prename, port)
            else:
                if len(instance_name) > 0:
                    wire = "%s_%s" % (instance_name, port)
                else:
                    wire = "%s" % port

        line = "\t.{0:<20}({1:<20})".format(port, wire)
        if port_count == port_max:
            buf += "%s\n" % line
        else:
            buf += "%s,\n" % line

    for port in inout_ports:
        port_count += 1
        line = ""
        #Special Case, we need to tie the specific signal directly to this port
        for key in slave_tags["bind"]:
            bname = key.partition("[")[0]
            bname.strip()
            if debug: print "Checking: %s" % bname
            if bname == port:
                loc = slave_tags["bind"][key]["loc"]
                if port_count == port_max:
                    buf += "\t.{0:<20}({1:<20})\n".format(port, loc)
                else:
                    buf += "\t.{0:<20}({1:<20}),\n".format(port, loc)


    buf += ");"
    return string.expandtabs(buf, 2)

def generate_assigns_buffer(invert_reset, bindings, internal_bindings, debug=False):
    buf = ""
    if len(internal_bindings) > 0:
        buf += "//Internal Bindings\n"
        for key in internal_bindings:
            if key == "clk":
                continue
            if key == "rst":
                continue

            if key == internal_bindings[key]["signal"]:
                pass

            buf += "assign\t{0:<20}=\t{1};\n".format(key, internal_bindings[key]["signal"])

    buf += "\n\n"
    if len(bindings) > 0:
        buf += "//Bindings\n"
        for key in bindings:
            if key == "clk":
                continue
            if key == "rst":
                continue


            if key == bindings[key]["loc"]:
                continue
            if bindings[key]["direction"] == "input":
                buf += "assign\t{0:<20}=\t{1};\n".format(key, bindings[key]["loc"])
            elif bindings[key]["direction"] == "output":
                buf += "assign\t{0:<20}=\t{1};\n".format(bindings[key]["loc"], key)

    if invert_reset:
        buf += "\n"
        buf += "//Invert Reset for this board\n"
        buf += "assign\t{0:<20}=\t{1};\n".format("rst_n", "~rst")

    return string.expandtabs(buf, 2)


class WishboneTopGenerator(object):
    def __init__(self):
        f = open(PATH_TO_TOP, "r")
        self.user_paths = []
        self.buf = f.read()
        self.internal_bindings = {}
        self.bindings = {}
        self.enable_mem_bus = False
        self.slave_list = {}
        self.tags = {}
        self.num_slaves = 0
        self.wires = []

    def generate_simple_top(self,
                            project_tags = {},
                            user_paths = [],
                            debug = False):
        self.tags = copy.deepcopy(project_tags)

        #Setup values
        self.user_paths = user_paths
        board_dict = utils.get_board_config(self.tags["board"])
        invert_reset = board_dict["invert_reset"]
        self.enable_mem_bus = False
        self.slave_list = self.tags["SLAVES"]

        if debug:
            print "Found %s slaves" % str(len(self.slave_list))
            for slave in self.slave_list:
                print "\t%s" % slave


        if "MEMORY" in self.tags:
            if len(self.tags["MEMORY"]) > 0:
                    if debug: print "Found %d Memory Devices" % len(self.tags["MEMORY"])
                    for mem in self.tags["MEMORY"]:
                        if debug: print "\t%s" % mem


                    enable_memory_bus = True
        self.num_slaves = len(self.slave_list) + 1


        self.internal_bindings = {}
        if "board_internal_bind" in self.tags:
            self.internal_bindings = self.tags["board_internal_bind"]

        #Extend the internal bindings
        if "internal_bind" in self.tags:
            for key in self.tags["internal_bind"]:
                self.internal_bindings[key] = self.tags["internal_bind"][key]

        #Add Global Bindings
        if "board_bind" in self.tags:
            self.bindings = self.tags["board_bind"]

        if "bind" not in self.tags:
            self.tags["bind"] = {}

        for key in self.tags["bind"]:
            self.bindings[key] = self.tags["bind"][key]

        #Add the Host Interface Bindings
        if "bind" in self.tags["INTERFACE"]:
            for name in self.tags["INTERFACE"]["bind"]:
                self.bindings[name] = self.tags["INTERFACE"]["bind"][name]

        #Add all the slave bindings
        for name in self.tags["SLAVES"]:
            if "bind" in self.tags["SLAVES"][name]:
                for bind_name in self.tags["SLAVES"][name]["bind"]:
                    bname = "%s_%s" % (name, bind_name)
                    self.bindings[bname] = self.tags["SLAVES"][name]["bind"][bind_name]

        #Add all the memory bindings
        if "MEMORY" in self.tags:
            for name in self.tags["MEMORY"]:
                if "bind" in self.tags["MEMORY"][name]:
                    for bind_name in self.tags["MEMORY"][name]["bind"]:
                        bname = "%s_%s" % (name, bind_name)
                        self.bindings[bname] = self.tags["MEMORY"][name]["bind"][bind_name]

        #Remove all ports from the possible wires
        self.add_ports_to_wires()

        #defines
        define_buf = ""
        if "defines" in self.tags:
            define_buf = generate_defines(self.tags["defines"])

        #If there is an infrastructure, generate the infrastructure buffer
        inf_buf = ""
        if "infrastructure" in self.tags:
            inf_buf = "//Infrastructures\n\n"
            for platform_inf_dict in self.tags["infrastructure"]:
                name = platform_inf_dict.keys()[0]
                inf_dict = platform_inf_dict[name]
                inf_buf += self.generate_infrastructure_buffer(name, inf_dict)
                if "bind" in inf_dict:
                    for bind_name in inf_dict["bind"]:
                        self.bindings[bind_name] = inf_dict["bind"][bind_name]


        #Setting up ports
        arb_buf = self.generate_arbiter_buffer(debug = debug)
        num_slaves = len(self.tags["SLAVES"]) + 1
        num_mem_slaves = 0
        if "MEMORY" in self.tags:
            if len(self.tags["MEMORY"]) > 0:
                num_mem_slaves = len(self.tags["MEMORY"])

        bp_buf  = self.generate_boilerplate_wires(invert_reset,
                                                  num_slaves,
                                                  num_mem_slaves,
                                                  debug = debug)
        hi_buf = self.generate_host_interface_buffer(debug = debug)
        slave_buffer_list = []

        #Add SDB
        slave_index = 0
        absfilename = utils.find_rtl_file_location("sdb.v", self.user_paths)
        slave_tags = vutils.get_module_tags(filename = absfilename,
                                           bus = "wishbone",
                                           user_paths = self.user_paths,
                                           project_tags = self.tags)
        slave_buf = self.generate_wishbone_buffer(name = "sdb",
                                                  index = 0,
                                                  slave_tags = {},
                                                  module_tags = slave_tags)
        slave_buffer_list.append(slave_buf)


        #Add the rest of the slaves
        for i in range (len(self.tags["SLAVES"])):
            slave_name = self.tags["SLAVES"].keys()[i]
            slave = self.tags["SLAVES"][slave_name]["filename"]
            if debug: "slave name: %s" % slave_name
            absfilename = utils.find_rtl_file_location(slave, self.user_paths)
            slave_tags = vutils.get_module_tags(filename = absfilename,
                                               bus = "wishbone",
                                               user_paths = self.user_paths,
                                               project_tags = self.tags)

            slave_buf = self.generate_wishbone_buffer(slave_name,
                                                      index = i + 1,
                                                      slave_tags = self.tags["SLAVES"][slave_name],
                                                      module_tags = slave_tags,
                                                      mem_slave = False)
            slave_buffer_list.append(slave_buf)

        #If there are memory slaves add them
        mem_buffer_list = []
        num_mem_slaves = 0
        if "MEMORY" in self.tags:
            num_mem_slaves = len(self.tags["MEMORY"])
            mem_index = 0
            for i in range(len(self.tags["MEMORY"])):
                mem_name = self.tags["MEMORY"].keys()[i]
                filename = self.tags["MEMORY"][mem_name]["filename"]
                if debug: print "Mem device: %s, mem file: %s" % (mem_name, filename)
                absfilename = utils.find_rtl_file_location(filename, self.user_paths)
                mem_tags = vutils.get_module_tags(filename = absfilename,
                                                 bus = "wishbone",
                                                 user_paths = self.user_paths,
                                                 project_tags = self.tags)
                mem_buf = self.generate_wishbone_buffer(mem_name,
                                                        index = i,
                                                        slave_tags = self.tags["MEMORY"][mem_name],
                                                        module_tags = mem_tags,
                                                        mem_slave = True)
                mem_buffer_list.append(mem_buf)


        #Add the ports
        buf = "//Top HDL\n"
        buf += "\n\n"
        buf += define_buf
        buf += "\n\n"
        buf +=  self.generate_top_ports(debug = debug)
        buf += "\n\n"
        #Add the boiler plate register/wires
        buf += bp_buf
        buf += "\n\n"
        #Add the startup
        buf += generate_startup()
        buf += "\n\n"
        #Add the infrastructure
        buf += inf_buf
        buf += "\n\n"
        #Add the master
        buf += generate_master_buffer(invert_reset)
        buf += "\n\n"
        #Add the host interface
        buf += hi_buf
        buf += "\n\n"
        #Add the peripheral interconnect
        buf += generate_peripheral_wishbone_interconnect_buffer(num_slaves, invert_reset)
        buf += "\n\n"
        #Add The memory interconnect
        buf += generate_memory_wishbone_interconnect_buffer(num_mem_slaves, invert_reset)
        buf += "\n\n"
        #Add an aritor if there is any
        buf += arb_buf
        buf += "\n\n"
        for slave_buf in slave_buffer_list:
            buf += slave_buf
            buf += "\n\n"
        for mem_buf in mem_buffer_list:
            buf += mem_buf
            buf += "\n\n"

        #Add assign statements
        buf += generate_assigns_buffer(invert_reset,
                                            self.bindings,
                                            self.internal_bindings,
                                            debug = debug)
        buf += "\n\n"

        buf += "endmodule"

        return string.expandtabs(buf, 2)

    def add_ports_to_wires(self):
        """Add all the ports to wires list so that no item adds extra wires"""
        for name in self.bindings:
            self.wires.append(self.bindings[name]["loc"])

    def generate_boilerplate_wires(self, invert_rst, num_slaves, num_mem_slaves, debug = False):
        board_dict = utils.get_board_config(self.tags["board"])

        buf =  "//General Signals\n"
        if "clkbuf" not in board_dict:
            if "clk" not in self.bindings:
                buf +=  "{0:<20}{1};\n".format("wire", "clk")

        else:
            if "clk" in self.bindings:
                del self.bindings["clk"]

        if "rst" not in self.bindings:
            buf +=  "{0:<20}{1};\n".format("wire", "rst")

        buf +=  "\n"
        buf +=  "//master synchronous inband reset\n"
        buf +=  "{0:<20}{1};\n".format("wire", "mstr_rst")


        if "clkbuf" in board_dict:
            buf += "{0:<20}{1};\n".format("wire", "clk")

        self.wires.append("rst")
        self.wires.append("clk")

        if invert_rst:
            buf += "{0:<20}{1};\n".format("wire", "rst_n")
            self.wires.append("rst_n")

        buf += "\n"
        buf +=  "//input handler signals\n"
        buf +=  "{0:<19}{1};\n".format("wire\t","ingress_clk")
        self.wires.append("ingress_clk")
        buf +=  "{0:<19}{1};\n".format("wire\t[1:0]","ingress_rdy");
        self.wires.append("ingress_rdy")
        buf +=  "{0:<19}{1};\n".format("wire\t[1:0]","ingress_act");
        self.wires.append("ingress_act")
        buf +=  "{0:<19}{1};\n".format("wire\t","ingress_stb");
        self.wires.append("ingress_stb")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","ingress_data")
        self.wires.append("ingress_data")
        buf +=  "{0:<19}{1};\n".format("wire\t[23:0]","ingress_size")
        self.wires.append("ingress_size")


        buf +=  "//output handler signals\n"
        buf +=  "{0:<20}{1};\n".format("wire","egress_clk")
        self.wires.append("egress_clk")
        buf +=  "{0:<20}{1};\n".format("wire","egress_rdy")
        self.wires.append("egress_rdy")
        buf +=  "{0:<20}{1};\n".format("wire","egress_act")
        self.wires.append("egress_act")
        buf +=  "{0:<20}{1};\n".format("wire","egress_stb")
        self.wires.append("egress_stb")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","egress_data")
        self.wires.append("egress_data")
        buf +=  "{0:<19}{1};\n".format("wire\t[23:0]","egress_size")
        self.wires.append("egress_size")


        buf +=  "//master signals\n"
        buf +=  "{0:<20}{1};\n".format("wire","master_ready")
        self.wires.append("master_ready")
        buf +=  "{0:<20}{1};\n".format("wire","wbm_we_o")
        self.wires.append("wbm_we_o")
        buf +=  "{0:<20}{1};\n".format("wire","wbm_cyc_o")
        self.wires.append("wbm_cyc_o")
        buf +=  "{0:<20}{1};\n".format("wire","wbm_stb_o")
        self.wires.append("wbm_stb_o")
        buf +=  "{0:<19}{1};\n".format("wire\t[3:0]","wbm_sel_o")
        self.wires.append("wbm_sel_o")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","wbm_adr_o")
        self.wires.append("wbm_adr_o")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","wbm_dat_i")
        self.wires.append("wbm_dat_i")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","wbm_dat_o")
        self.wires.append("wbm_dat_o")
        buf +=  "{0:<20}{1};\n".format("wire","wbm_ack_i")
        self.wires.append("wbm_ack_i")
        buf +=  "{0:<20}{1};\n".format("wire","wbm_int_i")
        self.wires.append("wbm_int_i")

        buf +=  "{0:<20}{1};\n".format("wire","mem_we_o")
        self.wires.append("mem_we_o")
        buf +=  "{0:<20}{1};\n".format("wire","mem_cyc_o")
        self.wires.append("mem_cyc_o")
        buf +=  "{0:<20}{1};\n".format("wire","mem_stb_o")
        self.wires.append("mem_stb_o")
        buf +=  "{0:<19}{1};\n".format("wire\t[3:0]","mem_sel_o")
        self.wires.append("mem_sel_o")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","mem_adr_o")
        self.wires.append("mem_adr_o")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","mem_dat_i")
        self.wires.append("mem_dat_i")
        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","mem_dat_o")
        self.wires.append("mem_dat_o")
        buf +=  "{0:<20}{1};\n".format("wire","mem_ack_i")
        self.wires.append("mem_ack_i")
        buf +=  "{0:<20}{1};\n".format("wire","mem_int_i")
        self.wires.append("mem_int_i")

        buf +=  "{0:<19}{1};\n".format("wire\t[31:0]","wbm_debug_out")
        self.wires.append("wbm_debug_out");
        buf +=  "\n"

        buf +=  "//slave signals\n\n"

        for i in range (0, num_slaves):
            buf +=  "//slave " + str(i) + "\n"
            wr_name = "s%d_i_wbs_we" % i
            buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_i_wbs_cyc" % i
            buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_i_wbs_dat" % i
            buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_o_wbs_dat" % i
            buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_i_wbs_adr" % i
            buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_i_wbs_stb" % i
            buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_i_wbs_sel" % i
            buf +=  "{0:<19}{1};\n".format("wire\t[3:0]", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_o_wbs_ack" % i
            buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

            wr_name = "s%d_o_wbs_int" % i
            buf +=  "{0:<20}{1};\n".format("wire", wr_name)
            self.wires.append(wr_name)

        if num_mem_slaves > 0:
            buf += "\n"
            for i in range (num_mem_slaves):
                buf +=  "//mem slave " + str(i) + "\n"
                wr_name = "sm%d_i_wbs_we" % i
                buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_i_wbs_cyc" % i
                buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_i_wbs_dat" % i
                buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_o_wbs_dat" % i
                buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_i_wbs_adr" % i
                buf +=  "{0:<19}{1};\n".format("wire\t[31:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_i_wbs_stb" % i
                buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_i_wbs_sel" % i
                buf +=  "{0:<19}{1};\n".format("wire\t[3:0]", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_o_wbs_ack" % i
                buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)

                wr_name = "sm%d_o_wbs_int" % i
                buf +=  "{0:<20}{1};\n".format("wire", wr_name)
                self.wires.append(wr_name)


        if debug:
            print "wr_buf: \n" + buf
        return string.expandtabs(buf, 2)

    def generate_internal_bindings(self):
        if len(self.internal_bindings.keys()) == 0:
            return ""

        buf = "//Internal assigns\n"
        #Generate the internal bindigns
        for key in self.internal_bindings:
            buf += "assign\t{0:20}=\t{1}:\n".format(key, self.internal_bindings[key]["signal"])
        return string.expandtabs(buf, 2)

    def generate_external_bindings(self, invert_reset):
        buf  = "//external assigns\n"
        board_dict = utils.get_board_config(self.tags["board"])
        for key in self.bindings:
            if key == self.bindings[key]["loc"]:
                #Don't need to bind this one skip it
                continue
            if self.bindings[key]["direction"] == "input":
                buf += "assign\t{0:20}=\t{1};\n".format(key, self.bindings[key]["loc"])
            elif self.bindings[key]["direction"] == "output":
                buf += "assign\t{0:20}=\t{1};\n".format(self.bindings[key]["loc"], key)

        if invert_reset:
            buf += "assign\t{0:<20}=\t{1};\n".format("rst_n", "~rst")
        return string.expandtabs(buf, 2)
        #Generate bindings that tie ports to wires

    def generate_bufg(self, clk_in):
        buf = "//Clock Buffer\n"
        buf += "BUFG clk_bufg(.I(%s), .O(clk));\n" % clk_in
        return buf

    def generate_top_ports(self, debug = False):
        """Create the ports string"""
        buf = "module top (\n"
        blist = self.bindings.keys()
        for i in range (len(blist)):
            name = blist[i]
            port_name = self.bindings[name]["loc"]
            eol = ""
            if i < len(blist) - 1:
                eol = ","
            if "[" in port_name and ":" in port_name:
                port_name = "[{0:<9}{1}".format(port_name.partition("[")[2], port_name.partition("[")[0])
            else:
                port_name = "{0:<10}{1}".format("", port_name)
            buf += "\t{0:10}\t{1}{2}\n".format(self.bindings[name]["direction"], port_name, eol)

        buf += ");"
        if debug: print "port buffer:\n%s" % buf
        return string.expandtabs(buf, 2)

    def generate_host_interface_buffer(self, debug = False):
        absfilepath = utils.find_rtl_file_location( self.tags["INTERFACE"]["filename"],
                                                    user_paths = self.user_paths)
        module_tags = vutils.get_module_tags(filename = absfilepath,
                                            bus = "wishbone",
                                            user_paths = self.user_paths,
                                            project_tags = self.tags)
        #print "module_tags: %s" % str(module_tags)
        name = "io"
        board_dict = utils.get_board_config(self.tags["board"])

        buf =  "// %s ( %s )\n\n" % (name, module_tags["module"])
        buf += "//wires\n"

        #Generate wires
        for io in IO_TYPES:
            if io == "inout":
                continue
            ports = module_tags["ports"][io]
            for port in ports:
                port_dict = ports[port]

                if port in IF_WIRES:
                    #This wire is already declared
                    continue

                if port in self.wires:
                    #This wire has already been declared somewhere else
                    continue

                #print "port: %s" % str(port)
                max_val = 0
                min_val = 0
                if port_dict["size"] > 1:
                    max_val = port_dict["max_val"]
                    min_val = port_dict["min_val"]
                buf += create_wire_buf(port,
                                       port_dict["size"],
                                       max_val,
                                       min_val)

        #Declare the Module
        buf += "\n\n"
        if "clkbuf" in board_dict:
            buf += self.generate_bufg(board_dict["clkbuf"])

        buf += "\n\n"
        buf += "%s\t%s\t" % (module_tags["module"], name)
        io_proj_tags = self.tags["INTERFACE"]
        invert_reset = utils.get_board_config(self.tags["board"])["invert_reset"]
        buf += generate_module_port_signals(invert_reset,
                                            "",
                                            "",
                                            self.tags["INTERFACE"],
                                            module_tags,
                                            host_interface = True)

        return string.expandtabs(buf, 2)

    def generate_wishbone_buffer(self,
                                 name="",
                                 index=-1,
                                 slave_tags = {},
                                 module_tags = {},
                                 mem_slave=False,
                                 debug=False):
        board_dict = utils.get_board_config(self.tags["board"])
        parameter_buffer = self.generate_parameters(name, slave_tags, debug)

        buf =  "// %s ( %s )\n\n" % (name, module_tags["module"])
        buf += "//Wires\n"

        #Check for an arbiter buffer
        arb_index = -1
        if "ARBITERS" in self.tags:
            if name in self.tags["ARBITERS"].keys():
                arb_index = self.tags["ARBITERS"].keys().index(name)

        #Generate wires
        pre_name = ""
        if (arb_index != -1):
            pre_name = "arb%d_" % arb_index
        else:
            if debug: print "no arbiter"

            if mem_slave:
                pre_name = "sm%d_" % index
            else:
                pre_name = "s%d_" % index

            if debug: print "pre name: %s" % pre_name

        for io in IO_TYPES:
            if io == "inout":
                continue

            for port in module_tags["ports"][io].keys():
                wire = ""
                port_dict = module_tags["ports"][io][port]
                if port == "clk" or port == "rst":
                    continue

                #if port in self.wires:
                #    if debug: print "%s is in wires already" % port
                #    continue

                if is_wishbone_slave_signal(port):
                    if debug: print "%s is a wishbone bus signal" % port
                    wire = "%s%s" % (pre_name, port)
                    if wire in self.wires:
                        if debug: print "%s is in wires already" % wire
                        continue
                else:
                    if debug: print "%s is NOT a wishbone bus signal" % port
                    wire = "%s_%s" % (name, port)
                    if wire in self.wires:
                        if debug: print "%s is in wires already" % wire
                        continue


                if wire in self.wires:
                    continue

                self.wires.append(port)


                max_val = 0
                min_val = 0
                if port_dict["size"] > 1:
                    max_val = port_dict["max_val"]
                    min_val = port_dict["min_val"]
                buf += create_wire_buf(wire,
                                       port_dict["size"],
                                       max_val,
                                       min_val)


            buf += "\n"

        buf += "%s " % module_tags["module"]
        buf += parameter_buffer
        buf += "\t%s" % name
        invert_reset = utils.get_board_config(self.tags["board"])["invert_reset"]
        buf += generate_module_port_signals(invert_reset,
                                            pre_name,
                                            name,
                                            slave_tags,
                                            module_tags)

        buf += "\n\n"
        return string.expandtabs(buf, 2)

    def generate_infrastructure_buffer(self, name, idict):
        buf = "//Infrastructure for %s\n\n" % name
        absfilename = utils.find_rtl_file_location(idict["filename"], self.user_paths)
        module_tags = vutils.get_module_tags(   filename = absfilename,
                                                user_paths = self.user_paths,
                                                project_tags = self.tags)
        board_dict = utils.get_board_config(self.tags["board"])
        buf += "//Wires\n"
        pre_name = ""
        for io in IO_TYPES:
            if io == "inout":
                continue

            ports = module_tags["ports"][io]
            for port in ports:
                port_dict = ports[port]
                if port == "clk" or port == "rst":
                    continue

                if port in self.wires:
                    continue

                self.wires.append(port)

                max_val = 0
                min_val = 0
                if port_dict["size"] > 1:
                    max_val = port_dict["max_val"]
                    min_val = port_dict["min_val"]
                buf += create_wire_buf(port,
                                       port_dict["size"],
                                       max_val,
                                       min_val)


            buf += "\n"

        buf += "%s %s_inf" % (module_tags["module"], name)
        invert_reset = board_dict["invert_reset"]
        buf += generate_module_port_signals(False,
                                            "",
                                            "",
                                            idict,
                                            module_tags,
                                            False)

        buf += "\n\n"
        #print "Generate buffer: %s" % buf
        return buf

    def generate_arbiter_buffer(self, debug = False):
        buf = ""
        board_dict = utils.get_board_config(self.tags["board"])
        arbiter_count = 0
        if not arbiter.is_arbiter_required(self.tags):
            return ""

        if debug: print "Arbiter is required"
        buf += "//Project Arbiters\n\n"

        arb_tags = arbiter.generate_arbiter_tags(self.tags)

        for i in range (len(arb_tags.keys())):
            arb_slave = arb_tags.keys()[i]
            master_count = 1

            if debug: print "Found arbiter slave: %s" % arb_slave
            buf += "//%s arbiter\n\n" % arb_slave
            master_count += len(arb_tags[arb_slave].keys())
            arb_name = "arb%s" % str(i)

            arb_module = "arbiter_%s_masters" % str(master_count)
            if debug:
                print "Number of masters for this arbiter: %d" % master_count
                print "Using: %s" % arb_module
                print "Arbiter name: %s" % arb_name


            #Generte the wires
            for mi in range (master_count):
                wbm_name = ""
                if mi == 0:
                    #These Wires are taken care of by the interconnect
                    continue

                master_name = arb_tags[arb_slave].keys()[mi - 1]
                bus_name = arb_tags[arb_slave][master_name]
                wbm_name = "%s_%s" % (master_name, bus_name)

                #Wishbone bus signals
                #strobe
                wire = "%s_o_stb" % wbm_name
                #print "Checking if %s is in %s" % (wire, self.wires)
                if not (wire in self.wires):
                    buf += "{0:<20}{1};\n".format("wire", wire)
                    self.wires.append(wire)
                #cycle
                wire = "%s_o_cyc" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<20}{1};\n".format("wire", wire)
                    self.wires.append(wire)
                #write enable
                wire = "%s_o_we" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<20}{1};\n".format("wire", wire)
                    self.wires.append(wire)
                #select
                wire = "%s_o_sel" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<19}{1};\n".format("wire\t[3:0]", wire)
                    self.wires.append(wire)
                #in data
                wire = "%s_o_dat" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                    self.wires.append(wire)
                #address
                wire = "%s_o_adr" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                    self.wires.append(wire)
                #out data
                wire = "%s_i_dat" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                    self.wires.append(wire)
                #acknowledge
                wire = "%s_i_ack" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<20}{1};\n".format("wire", wire)
                    self.wires.append(wire)
                #interrupt
                wire = "%s_i_int" % wbm_name
                if not (wire in self.wires):
                    buf += "{0:<20}{1};\n".format("wire", wire)
                    self.wires.append(wire)

            buf += "\n"
            #generate arbiter signals
            #strobe
            wire = "%s_i_wbs_stb" % arb_name
            if not (wire in self.wires):
                buf += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #cycle
            wire = "%s_i_wbs_cyc" % arb_name
            if not (wire in self.wires):
                buf += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #write enable
            wire = "%s_i_wbs_we" % arb_name
            if not (wire in self.wires):
                buf += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #select
            wire = "%s_i_wbs_sel" % arb_name
            if not (wire in self.wires):
                buf += "{0:<19}{1};\n".format("wire\t[3:0]", wire)
                self.wires.append(wire)
            #in data
            wire = "%s_i_wbs_dat" % arb_name
            if not (wire in self.wires):
                buf += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                self.wires.append(wire)
            #out data
            wire = "%s_o_wbs_dat" % arb_name
            if not (wire in self.wires):
                buf += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                self.wires.append(wire)
            #address
            wire = "%s_i_wbs_adr" % arb_name
            if not (wire in self.wires):
                buf += "{0:<19}{1};\n".format("wire\t[31:0]", wire)
                self.wires.append(wire)
            #acknowledge
            wire = "%s_o_wbs_ack" % arb_name
            if not (wire in self.wires):
                buf += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)
            #interrupt
            wire = "%s_o_wbs_int" % arb_name
            if not (wire in self.wires):
                buf += "{0:<20}{1};\n".format("wire", wire)
                self.wires.append(wire)

            buf +="\n\n"


            #finished generating the wires

            buf += "%s %s (\n" % (arb_module, arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("clk", "clk")
            if board_dict["invert_reset"]:
                buf += "\t.{0:20}({1:20}),\n".format("rst", "rst_n | startup_rst")
            else:
                buf += "\t.{0:20}({1:20}),\n".format("rst", "rst | startup_rst")
            buf += "\n"

            buf += "\t//masters\n"

            for mi in range(master_count):
                wbm_name = ""

                #Last master is always from the interconnect
                #XXX: This should really be a parameter, but this will allow slaves to take over a peripheral
                if (mi == master_count - 1):
                    if debug: print "mi: %d" % mi
                    on_periph_bus = False
                    #in this case I need to use the wishbone interonnect
                    #search for the index of the slave
                    for i in range (len(self.tags["SLAVES"].keys())):
                        name = self.tags["SLAVES"].keys()[i]
                        if name == arb_slave:
                            interconnect_index = i + 1 # +1 to account for the SDB
                            on_periph_bus = True
                            wbm_name = "s" + str(interconnect_index)
                            if debug:
                                print "arb slave on peripheral bus"
                                print "slave index: %d" % interconnect_index - 1
                                print "account for the sdb, actual bus index: %d" % interconnect_index
                            break
                    if not on_periph_bus:
                        if "MEMORY" in self.tags:
                            #There is a memory bus, look in here
                            for i in range (len(self.tags["MEMORY"].keys())):
                                    name = self.tags["MEMORY"].keys()[i]
                                    if name == arb_slave:
                                        mem_inc_index = i
                                        wbm_name = "sm%d" % i
                                        if debug:
                                            print "arb slave on mem bus"
                                            print "slave index: %d" % mem_inc_index
                                        break

                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_we"  % mi, "%s_i_wbs_we" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_stb" % mi, "%s_i_wbs_stb" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_cyc" % mi, "%s_i_wbs_cyc" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_sel" % mi, "%s_i_wbs_sel" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_dat" % mi, "%s_i_wbs_dat" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_adr" % mi, "%s_i_wbs_adr" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("o_m%d_dat" % mi, "%s_o_wbs_dat" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("o_m%d_ack" % mi, "%s_o_wbs_ack" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("o_m%d_int" % mi, "%s_o_wbs_int" % wbm_name)

                    buf +="\n\n"
                else:
                    if debug: print "mi: %d" % mi
                    master_name = arb_tags[arb_slave].keys()[mi]
                    bus_name = arb_tags[arb_slave][master_name]
                    wbm_name = "%s_%s" % (master_name, bus_name)

                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_we" % mi,  "%s_o_we" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_stb" % mi, "%s_o_stb" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_cyc" % mi, "%s_o_cyc" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_sel" % mi, "%s_o_sel" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_dat" % mi, "%s_o_dat" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("i_m%d_adr" % mi, "%s_o_adr" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("o_m%d_dat" % mi, "%s_i_dat" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("o_m%d_ack" % mi, "%s_i_ack" % wbm_name)
                    buf +="\t.{0:20}({1:20}),\n".format("o_m%d_int" % mi, "%s_i_int" % wbm_name)
                    buf +="\n\n"


            buf += "\t//slave\n"
            buf += "\t.{0:20}({1:20}),\n".format("o_s_we",  "%s_i_wbs_we"  % arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("o_s_stb", "%s_i_wbs_stb" % arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("o_s_cyc", "%s_i_wbs_cyc" % arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("o_s_sel", "%s_i_wbs_sel" % arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("o_s_dat", "%s_i_wbs_dat" % arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("o_s_adr", "%s_i_wbs_adr" % arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("i_s_dat", "%s_o_wbs_dat" % arb_name)
            buf += "\t.{0:20}({1:20}),\n".format("i_s_ack", "%s_o_wbs_ack" % arb_name)
            buf += "\t.{0:20}({1:20})\n".format( "i_s_int", "%s_o_wbs_int" % arb_name)
            buf += ");\n"

            return string.expandtabs(buf, 2)

    def generate_parameters(self, name="", slave_tags={}, debug = False):
        buf = ""
        if not (name in self.tags["SLAVES"]):
            if debug: print "Didn't find %s in slave list" % name
            return ""

        if debug: print "Check to see if %s contains parameter in config file" % name
        if not ("PARAMETERS" in self.tags["SLAVES"][name]):
            if debug: print "\tno"
            return ""

        if debug: print "\tyes"

        if debug: print "check to see if the module contains parameters..."
        if len(slave_tags["PARAMETERS"].keys()) == 0:
            if debug: print "\tno"
            return ""

        if debug: print "\tyes"
        module_parameters = slave_tags["PARAMETERS"]
        buf = "#(\n"
        project_parameters =self.tags["SLAVES"][name]["PARAMETERS"]
        first_item = True
        for project_param in project_parameters:
            if project_param in module_parameters:
                if first_item == False:
                    buf += ",\n"
                first_item = False
                if debug: print "Found that %s is a match" % project_param
                buf += "\t.{0:10}\t({1:10})".format(project_param, project_parameters[project_param])
                #buf += "\t\t.%s(%s)" % (project_param, project_parameters[project_param])

        #Finish off the buffer
        buf += "\n)\n"
        return string.expandtabs(buf, 2)


