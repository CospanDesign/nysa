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

"""sim_utils

Utilities used to generate simulation interfaces

"""

"""
Changes:
9/16/2013
    -Initial Commit
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import json
import string
import shutil

#Project Modules
import utils
import verilog_utils as vutils
import module_builder as mb
import ibuilder_error

class SimUtilsError(ibuilder_error.IBuilderError):
    pass


SIM_EXTENSION = ".json"
sim_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        os.pardir,
                                        "sim"))

def get_sim_module_dict(module_name, user_paths = [], debug = False):
    """
    Get the sim module tags associated with the specified name

    takes in a name of a module to be tested, E.G. 'wb_sdram' and searches
    for a configuration file that can be used to setup a test for this module

    Args:
        module_name (string): name of the module that is to be tested.
        user_paths (list of strings): paths to prepend to the search directory
            when looking for modules

    Returns:
        (dict): A dictionary of module tags that will be used to build a
            simulation interface

    Raises:
        SimUtilsError:
                -Sim File was not found
                -A user path was not valit
        TypeError:
                -Pass JSON Errors up
        ValueError
                -Pass JSON Errors up
    """
    paths = user_paths
    paths.append(sim_path)
    sim_filename = "%s.%s" % (module_name, SIM_EXTENSION)
    #Setinal value to catch if the path to the sim module dict doesn't exist
    sim_filepath = None
    found_path = False
    for path in paths:
        if found_path:
            #Fond the first occurance of the file we're looking for
            break
        if not os.path.exists(path):
            raise SimUtilsError("sim_utils: path: %s is not a valid" % path)
        if not os.path.isdir(path):
            raise SimUtilsError("sim_utils: path %s is not a directory" % path)

        for root, dirs, names in os.walk(path):
            for sim_filename in names:
                sim_filepath = os.path.abspath(os.path.join(root, sim_filename))
                #Drop out of the outer loop too (double break!)
                found_path = True
                break

    #Check if we captured something
    if sim_filepath is None:
        raise SimUtilsError("sim_utils: did not find %s" % sim_filename,
                            "searched: %s" % str(paths))
    sim_dict = None
    try:
        fp = open(sim_filepath, "r")
        #print "Open: %s" % sim_filepath
        sim_dict = json.loads(fp.read())
        fp.close()
    except IOError, err:
        raise SimUtilsError("sim_utils: Failed to open file %s: Error: %s" %
                (sim_filepath, str(err)))


    return sim_dict

def add_sim_modules_to_project(tags, sim_dict, user_paths):
    #utils.pretty_print_dict(tags)
    #utils.pretty_print_dict(sim_dict)
    #Get the directory of where to put the sim modules
    base_dir = utils.resolve_path(tags["BASE_DIR"])
    project_dir = tags["PROJECT_NAME"]
    out_dir = os.path.join(base_dir, "sim", "sim_modules")
    if not os.path.exists(out_dir):
        utils.create_dir(out_dir)


    #Find all the file locations
    module_filename = utils.find_module_filename(sim_dict["name"], user_paths)
    module_filepath = utils.find_rtl_file_location(module_filename, user_paths)

    out_file_path = os.path.join(out_dir, module_filename)
    #print "copy %s > %s" % (module_filepath, out_file_path)
    shutil.copy2(module_filepath, os.path.join(out_dir, out_file_path))

    #Get the locations for each of the auxilary files
    for f in sim_dict["aux_files"]:
        module_path = utils.find_rtl_file_location(f)
        out_file_path = os.path.join(out_dir, f)
        #print "copy %s > %s" % (module_path, out_file_path)
        shutil.copy2(module_path, os.path.join(out_dir, f))





def get_bind_direction(signal, module_tags):
    #We have a signal and a location to bind it, we need the direction
    if "input" in module_tags["ports"]:
        for port in module_tags["ports"]["input"]:
            if port == signal:
                return "input"
    if "output" in module_tags["ports"]:
        for port in module_tags["ports"]["output"]:
            if port == signal:
                return "output"

    if "inout" in module_tags["ports"]:
        for port in module_tags["ports"]["inout"]:
            if port == signal:
                return "inout"

def generate_sub_slave_dict(sim_dict, debug = False):
    #Get sim module tags
    filename = utils.find_module_filename(sim_dict["name"])
    filepath = utils.find_rtl_file_location(filename)
    sim_tags = vutils.get_module_tags(filepath)
    bind_dict = sim_tags["ports"]
    sim_tags["bind"] = {}
    #Go through each dictionary entry and determine the direction
    for signal in sim_dict["bind"]:
        #XXX: Don't support subset of busses yet
        sim_tags["bind"][signal] = {}
        sim_tags["bind"][signal]["loc"] = sim_dict["bind"][signal]
        sim_tags["bind"][signal]["direction"] = get_bind_direction(signal, sim_tags)

    return sim_tags

def generate_tb_module(tags, top_buffer, user_paths = [], debug=False):
    """
    Generate the test bench

    Args:
        tags (dictionary): Dictionary defining a project
        top_buffer (string): A buffer of the top module
        user_paths (list of strings): a list of paths pointing to user
            directories

    Returns:
        (string): buffer of the test module

    Raises:
        Nothing
    """

    top_module_tags = vutils.get_module_buffer_tags(top_buffer,
                                                    bus = "wishbone",
                                                    user_paths = [])
    top_module = {
        "bind":{
            "sim_in_reset":{
                "loc":"i_sim_in_reset",
                "direction":"input",
                "reg":True
            },
            "sim_in_ready":{
                "loc":"i_sim_in_ready",
                "direction":"input",
                "reg":True
            },
            "sim_in_command":{
                "loc":"i_sim_in_command",
                "direction":"input",
                "reg":True
            },
            "sim_in_address":{
                "loc":"i_sim_in_address",
                "direction":"input",
                "reg":True
            },
            "sim_in_data":{
                "loc":"i_sim_in_data",
                "direction":"input",
                "reg":True
            },
            "sim_in_data_count":{
                "loc":"i_sim_in_data_count",
                "direction":"input",
                "reg":True
            },

            "sim_master_ready":{
                "loc":"o_sim_master_ready",
                "direction":"output"
            },
            "sim_out_en":{
                "loc":"o_sim_out_en",
                "direction":"output"
            },
            "sim_out_status":{
                "loc":"o_sim_out_status",
                "direction":"output"
            },
            "sim_out_address":{
                "loc":"o_sim_out_address",
                "direction":"output"
            },
            "sim_out_data":{
                "loc":"o_sim_out_data",
                "direction":"output"
            },
            "sim_out_data_count":{
                "loc":"o_sim_out_data_count",
                "direction":"output"
            }
        }
    }
    top_module["ports"] = {}
    top_module["ports"] = top_module_tags["ports"]
    top_module["module"] = top_module_tags["module"]
    #print "top module tags:\n"
    #utils.pretty_print_dict(top_module)



    invert_reset = utils.get_board_config(tags["board"])
    sim_modules = {}
    if "SLAVES" in tags:
        for slave in tags["SLAVES"]:
            if "sim" in tags["SLAVES"][slave]:
                module_name = tags["SLAVES"][slave]["filename"].strip(".v")
                sim_dict = get_sim_module_dict(module_name,
                                               user_paths)
                add_sim_modules_to_project(tags, sim_dict, user_paths)
                sim_modules[slave] = generate_sub_slave_dict(sim_dict)


    if "MEMORY" in tags:
        for mem in tags["MEMORY"]:
            if "sim" in tags["MEMORY"][mem]:
                module_name = tags["MEMORY"][mem]["filename"].strip(".v")
                sim_dict = get_sim_module_dict(module_name,
                                               user_paths)
                add_sim_modules_to_project(tags, sim_dict, user_paths)
                sim_modules[mem] = generate_sub_slave_dict(sim_dict)

    tb_tags = {}
    tb_tags["module"] = "tb"

    #ports = tb_tags["ports"]
    ports = {}
    ports["input"] = {}
    ports["output"] = {}
    ports["inout"] = {}

    ports["input"]["clk"] = {
        "direction":"input",
        "size":1
    }
    ports["input"]["rst"] = {
        "direction":"input",
        "size":1
    }
    ports["input"]["i_sim_in_reset"]= {
        "direction":"input",
        "size":1
    }
    ports["input"]["i_sim_in_ready"] = {
        "direction":"input",
        "size":1
    }
    ports["input"]["i_sim_in_command"] = {
        "direction":"input",
        "size":32,
        "min_val":0,
        "max_val":31
    }
    ports["input"]["i_sim_in_address"] = {
        "direction":"input",
        "size":32,
        "min_val":0,
        "max_val":31
    }
    ports["input"]["i_sim_in_data"] = {
          "direction":"input",
        "size":32,
        "min_val":0,
        "max_val":31
    }
    ports["input"]["i_sim_in_data_count"] = {
        "direction":"input",
        "size":32,
        "min_val":0,
        "max_val":31
    }
    ports["output"]["o_sim_master_ready"] = {
        "direction":"output",
        "size":1
    }
    ports["output"]["o_sim_out_en"] = {
        "direction":"output",
        "size":1
    }
    ports["output"]["o_sim_out_status"] = {
        "direction":"output",
        "size":32,
        "min_val":0,
        "max_val":31
    }
    ports["output"]["o_sim_out_address"] = {
        "direction":"output",
        "size":32,
        "min_val":0,
        "max_val":31
    }
    ports["output"]["o_sim_out_data"] = {
        "direction":"output",
        "size":32,
        "min_val":0,
        "max_val":31
    }

    ports["output"]["o_sim_out_data_count"] = {
        "direction":"output",
        "size":32,
        "min_val":0,
        "max_val":31
    }
    tb_tags["ports"] = ports


    #if debug:
    #    utils.pretty_print_dict(tb_tags)
    MB = TBModuleBuilder(tb_tags)
    #Generate 'slave_tags' or tags we will use to bind ports to simulation
    #Add the ports to the wires
    MB.add_ports_to_wires()
    sub_buffers = []
    sub_buffers.append(MB.generate_sub_module(
                        invert_reset,
                        "top",
                        top_module,
                        top_module,
                        enable_unique_ports = False))


    for sim in sim_modules:
        sub_buffers.append(MB.generate_sub_module(
                            invert_reset,
                            sim,
                            sim_modules[sim],
                            sim_modules[sim]))

    assign_buf = generate_assigns_buffer(invert_reset,
                                         MB.bindings,
                                         internal_bindings = {},
                                         debug = False)
    buf =  mb.generate_timespec_buf()
    buf += mb.generate_module_ports("tb",
                                    MB.tags["ports"],
                                    param_dict = {},
                                    debug = False)
    buf += "\n"
    buf += MB.generate_module_wires(invert_reset)
    buf += generate_top_inout_wires(top_module)
    for sub in sub_buffers:
        buf += sub
        buf += "\n"

    buf += "\n"
    buf += assign_buf
    buf += "\n"

    buf += ("\n" +
        "initial begin\n"
        "  $dumpfile (\"waveform.vcd\");\n" +
        "  $dumpvars (0, tb);\n" +
        "end\n\n")


    buf += "endmodule"
                                    
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
                continue

            buf += "assign\t{0:<20}=\t{1};\n".format(key, internal_bindings[key]["signal"])

    buf += "\n\n"
    if len(bindings) > 0:
        buf += "//Bindings\n"
        buf += "always @ (*) begin\n"

        for key in bindings:
            if key == "clk":
                continue
            if key == "rst":
                continue
            if key == bindings[key]["loc"]:
                continue

            if (bindings[key]["direction"] == "input") and ("reg" in bindings[key]):
                buf += "\t{0:<20}=\t{1};\n".format(key, bindings[key]["loc"])
                #buf += "assign\t{0:<20}=\t{1};\n".format(key, bindings[key]["loc"])

        buf += "end\n" 
        for key in bindings:
            if key == "clk":
                continue
            if key == "rst":
                continue
            if key == bindings[key]["loc"]:
                continue

            if (bindings[key]["direction"] == "input") and ("reg" not in bindings[key]):
                buf += "assign\t{0:<20}=\t{1};\n".format(key, bindings[key]["loc"])

        for key in bindings:
            if key == bindings[key]["loc"]:
                continue


            if bindings[key]["direction"] == "output":
                buf += "assign\t{0:<20}=\t{1};\n".format(bindings[key]["loc"], key)


    if invert_reset:
        buf += "\n"
        buf += "//Invert Reset for this board\n"
        buf += "always @ (*) begin\n"
        buf += "\t{0:<20}=\t{1};\n".format("rst_n", "~rst")
        buf += "end\n"

    return string.expandtabs(buf, 2)



def generate_top_inout_wires(top_module):
    buf = "//Master inout wires\n"
    if "inout" in top_module["ports"]:
        for port in top_module["ports"]["inout"]:
            buf += vutils.create_wire_buf_from_dict(port, top_module["ports"]["inout"][port])

    return buf


class TBModuleBuilder(mb.ModuleBuilder):

    def __init__(self, tags = None):
        super(TBModuleBuilder, self).__init__(tags)

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

                if module_tags["module"] == "top":
                    buf += vutils.create_reg_buf_from_dict(pname,
                                                            module_tags["ports"]["input"][port])
                else:
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

    def generate_module_wires(self, invert_reset):
        buf = ""
        if invert_reset:
            buf += vutils.create_reg_buf("rst_n", 1, 0, 0)
        return buf


