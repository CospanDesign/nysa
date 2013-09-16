# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa (http://wiki.cospandesign.com/index.php?title=Nysa.org).
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

"""Utilities used to generate and extract information from Verilog cores"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'
import os
import sys
import string
import json
import arbitor

import utils
import preprocessor

def get_module_buffer_tags(buf="", bus="", keywords = [], user_paths = [], debug=False):
    raw_buf = buf
    tags = {}
    tags["keywords"] = {}
    tags["ports"] = {}
    tags["module"] = ""
    tags["parameters"] = {}
    tags["arbitor_masters"] = []
 
    ports = [
        "input",
        "output",
        "inout"
    ]
 
 
    #XXX only working with verilog at this time, need to extend to VHDL
    #print "filename: %s" % filename
 
    #find all the metadata
    for key in keywords:
        index = buf.find (key)
        if (index == -1):
            if debug:
                print "didn't find substring for " + key
            continue
        if debug:
          print "found substring for " + key
       
        substring = buf.__getslice__(index, len(buf)).splitlines()[0]
        if debug:
            print "substring: " + substring
       
       
        if debug:
            print "found " + key + " substring: " + substring
       
        substring = substring.strip()
        substring = substring.strip("//")
        substring = substring.strip("/*")
        tags["keywords"][key] = substring.partition(":")[2]
 
 
 
    #remove all the comments from the code
    buf = remove_comments(buf)
    #print "no comments: \n\n" + buf
 
    for substring in buf.splitlines():
        if (len(substring.partition("module")[1]) == 0):
            continue
        module_string = substring.partition("module")[2]
        module_string = module_string.strip(" ")
        module_string = module_string.strip("(")
        module_string = module_string.strip("#")
        index = module_string.find(" ")
       
        if (index != -1):
            tags["module"] = module_string.__getslice__(0, index)
        else:
            tags["module"] = module_string
       
        if debug:
            print "module name: " + module_string
            print tags["module"]
        break
 
    #find all the ports
    #find the index of all the processing block
    substrings = buf.splitlines()
 
    input_count = buf.count("input")
    output_count = buf.count("output")
    inout_count = buf.count("inout")
 
    ldebug = debug
    define_dict = preprocessor.generate_define_table(raw_buf, user_paths, ldebug)
 
    #find all the IO's
    for io in ports:
        tags["ports"][io] = {}
        substrings = buf.splitlines()
        for substring in substrings:
            substring = substring.strip()
            #if line doesn't start with an input/output or inout
            if (not substring.startswith(io)):
                continue
            #if the line does start with input/output or inout but is used in a name then bail
            if (not substring.partition(io)[2][0].isspace()):
                continue
            #one style will declare the port names after the ports list
            if (substring.endswith(";")):
                substring = substring.rstrip(";")
            #the other stile will include the entire port definition within the port declaration
            if (substring.endswith(",")):
                substring = substring.rstrip(",")
            if debug:
                print "substring: " + substring
            substring = substring.partition(io)[2]
            if (len(substring.partition("reg")[1]) != 0):
                substring = substring.partition("reg")[2]
            substring = substring.strip()
            max_val = -1
            min_val = -1
            if (len(substring.partition("]")[2]) != 0):
                #we have a range to work with?
                length_string = substring.partition("]")[0] + "]"
                substring = substring.partition("]")[2]
                substring = substring.strip()
                length_string = length_string.strip()
                if debug:
                    print "length string: " + length_string
               
                ldebug = debug
               
                length_string = preprocessor.resolve_defines(length_string, define_dict, debug=ldebug)
                length_string = preprocessor.evaluate_range(length_string)
                length_string = length_string.partition("]")[0]
                length_string = length_string.strip("[")
                if debug:
                    print "length string: " + length_string
                max_val = string.atoi(length_string.partition(":")[0])
                min_val = string.atoi(length_string.partition(":")[2])
           
            tags["ports"][io][substring] = {}
           
            if (max_val != -1):
                tags["ports"][io][substring]["max_val"] = max_val
                tags["ports"][io][substring]["min_val"] = min_val
                tags["ports"][io][substring]["size"] = (max_val + 1) - min_val
            else:
                tags["ports"][io][substring]["size"] = 1
       
    #find all the USER_PARAMETER declarations
    user_parameters = []
    substrings = raw_buf.splitlines()
    for substring in substrings:
        substring = substring.strip()
        if "USER_PARAMETER" in substring:
            name = substring.partition(":")[2].strip()
            user_parameters.append(name)
 
 
    #find all the parameters
    substrings = buf.splitlines()
    for substring in substrings:
        substring = substring.strip()
        if ("parameter" in substring):
            if debug:
                print "found parameter!"
            substring = substring.partition("parameter")[2].strip()
            parameter_name = substring.partition("=")[0].strip()
            parameter_value = substring.partition("=")[2].strip()
            parameter_value = parameter_value.partition(";")[0].strip()
            parameter_value = parameter_value.strip(',')
            if debug:
                print "parameter name: " + parameter_name
                print "parameter value: " + parameter_value
            if parameter_name in user_parameters:
                tags["parameters"][parameter_name] = parameter_value
 
 
    tags["arbitor_masters"] = arbitor.get_number_of_arbitor_hosts(tags)
 
 
    if debug:
        print "input count: " + str(input_count)
        print "output count: " + str(output_count)
        print "inout count: " + str(inout_count)
        print "\n"
 
    if debug:
        print "module name: " + tags["module"]
        for key in tags["keywords"].keys():
            print "key: " + key + ":" + tags["keywords"][key]
        for io in ports:
            for item in tags["ports"][io].keys():
                print io + ": " + item
                for key in tags["ports"][io][item].keys():
                    value = tags["ports"][io][item][key]
                    if (isinstance( value, int)):
                        value = str(value)
                    print "\t" + key + ":" + value
 
    return tags




def get_module_tags(filename="", bus="", keywords = [], user_paths = [], debug=False):
    """Gets the tags for the module within the specified filename
 
    Given a module within a filename search through the module and
    find:
      metadata
        \"DRT_ID\"
        \"DRT_FLAGS\"
      ports: Inputs/Outputs of this module
      module: Name of the module
      parameters: Configuration parameters within the module
      arbitor_masters: Any arbitor masters within the module
 
    Args:
      filename: Name of the module to interrogate
      bus: A string declaring the bus type, this can be
        \"wishbone\" or \"axie\"
      keywords:
        Besides the standard metadata any additional values to search for
 
    Returns:
      A dictionary of module tags
 
    Raises
      Nothing
    """
    buf = ""
    with open(filename) as slave_file:
        buf = slave_file.read()
 
    return get_module_buffer_tags(buf = buf,
                                  bus = buf,
                                  keywords = keywords,
                                  user_paths = user_paths,
                                  debug = debug)


def remove_comments(buf="", debug=False):
    """Remove comments from a buffer.
 
    Args:
      buf = Buffer to remove the comments from
 
    Returns:
      A buffer with no verilog comments in it
 
    Raises:
      Nothing
    """
    #first pass remove the '//' comments
    lines = buf.splitlines()
    if debug:
        print "buf:\n" + buf
    bufx = ""
    for line in lines:
        line = line.partition("//")[0]
        bufx = bufx + line + "\n"
    if debug:
        print "bufx:\n" + bufx
 
    if debug:
        print "working on /* */ comments\n\n\n"
    #get rid of /*, */ comments
    buf_part = bufx.partition("/*")
    pre_comment = ""
    post_comment = ""
    bufy = bufx
    while (len(buf_part[1]) != 0):
        pre_comment = buf_part[0]
        post_comment = buf_part[2].partition("*/")[2]
        #print "pre_comment: " + pre_comment
        #print "post comment: " + post_comment
        bufy = pre_comment + post_comment
        buf_part = bufy.partition("/*")
        pre_comment = ""
        post_comment = ""
 
    if debug:
        print "buf:\n" + bufy
 
    return bufy


