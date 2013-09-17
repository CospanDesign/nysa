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

#Project Modules
import utils
import verilog_utils as vutils
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

    #Check if we captures something
    if sim_filepath is None:
        raise SimUtilsError("sim_utils: did not find %s" % sim_filename,
                            "searched: %s" % str(paths))
    sim_dict = None
    try:
        fp = open(sim_filepath, "r")
        if debug: print "Open: %s" % sim_filepath
        sim_dict = json.loads(fp.read())
        fp.close()
    except IOError, err:
        raise SimUtilsError("sim_utils: Failed to open file %s: Error: %s" % 
                (sim_filepath, str(err)))


    return sim_dict
    

def generate_sim_module_buf(invert_reset,
                            instance_name,
                            sim_module_tags,
                            debug = False):
    """
    Generates a sim module buffer that is suitable to be put in the testbench

    Args:
        invert_reset (boolean):
            True: reset is inverted
            False: reset is not inverted
        sim_module_tags (dict): A dictionary of simulation tags used to
            generate the buffer
    
    Returns:
        (string): buffer that will instantiate the simulation module

    Raises:
        Nothing

    """
    #Look through the sim_module_tags for the inout ports
    nysa_base = utils.get_nysa_base()
    #search_path = os.path.join(nysa_base,
    #                           "cbuilder",
    #                           "verilog")
    #filename = utils.find_module_filename(sim_module_tags["name"], [search_path])
    filename = utils.find_module_filename(sim_module_tags["name"])
    if debug: print "Module filename: %s" % filename
    filepath = utils.find_rtl_file_location(filename)
    if debug: print "Module filepath: %s" % filepath
    module_tags = vutils.get_module_tags(filepath)
    #if debug: print "Module Tags: %s" % str(module_tags)
    #if debug: print "Ports: %s" % str(sim_module_tags["bind"].keys())

    bind_list = []

    for port in sim_module_tags["bind"].keys():
        #if debug: print "port: %s" % port
        #if debug: print "partition: %s" % str(port.partition("[")[0])
        if len(port.partition("[")[0]) > 0:
            name = port.partition("[")[0]
            if name not in bind_list:
                bind_list.append(name)
        else:
            if port not in bind_list:
                bind_list.append(port)

    #if debug:
    #    print "bind list:"
    #    for bind in bind_list:
    #        print "\t%s" % bind
    #    print ""
        
    #Need to fake out the verilog_utils port interface to thinking we are just a
    #   normal slave module with port declaration for the entire module
    inout_ports = {}
    inout_ports["bind"] = {}
    if "inout" in module_tags["ports"]:
        for inout_port in module_tags["ports"]["inout"]:
            #if debug: print "inout_port: %s" % str(inout_port)
            if inout_port not in sim_module_tags["bind"]:
                continue

            #inout_ports["bind"]["inout"] = module_tags["ports"]["inout"]
            inout_ports["bind"][inout_port] = {}

            inout_ports["bind"][inout_port]["loc"] = sim_module_tags["bind"][inout_port]

    if debug:
        print "inout ports"
        for inout in inout_ports["bind"]:
            print "\t%s:%s" % (inout, inout_ports["bind"][inout])

    buf = vutils.generate_module_port_signals(invert_reset,
                                              name = instance_name,
                                              prename = "",
                                              slave_tags = inout_ports,
                                              module_tags = module_tags)

    return buf
                                                
        

def generate_tb_module_ports():
    """
    Generate the test bench ports

    Args:
        Nothing

    Returns:
        (string): buffer of the test module ports

    Raises:
        Nothing
    """
    buf = ""
