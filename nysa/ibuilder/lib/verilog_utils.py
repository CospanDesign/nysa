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

"""Utilities used to generate and extract information from Verilog cores"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'
import os
import sys
import string
import json
import arbitor
import re

import utils
import preprocessor

def get_eol(total, index):
    if index < total:
        return ","
    return ""


def get_module_buffer_tags(buf="", bus="", keywords = [], user_paths = [], debug=False):
    raw_buf = buf
    tags = {}
    tags["keywords"] = {}
    tags["ports"] = {}
    tags["module"] = ""
    tags["parameters"] = {}
    tags["arbitor_masters"] = []

    in_task = False
    end_module = False

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
        end_module = False
        in_task = False

        tags["ports"][io] = {}
        substrings = buf.splitlines()
        for substring in substrings:
            substring = substring.strip()
            if substring.startswith("endmodule"):
                end_module = True
                continue
            #Only count one module per buffer
            if end_module:
                continue

            if substring.startswith("task"):
                #Sub tasks and functions declare inputs and outputs, don't count these
                in_task = True
                continue
            if substring.startswith("function"):
                in_task = True
                continue

            if substring.startswith("endtask"):
                in_task = False
                continue

            if substring.startswith("endfunction"):
                in_task = False
                continue

            if in_task:
                continue

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
                if (len(substring.partition("reg")[0]) > 0) and  \
                        (substring.partition("reg")[0][-1].isspace()):
                    #print "Substring: %s" % substring
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

def generate_module_port_signals(invert_reset,
                                 name = "",
                                 prename = "",
                                 slave_tags = {},
                                 module_tags = {},
                                 wishbone_slave = False,
                                 debug = False):

    buf = ""
    if ("parameters" in module_tags) and \
            len(module_tags["parameters"].keys()) > 0:
        buf = "%s #(\n" % module_tags["module"]
        num_params = len(module_tags["parameters"])
        param_count = 1
        for param in module_tags["parameters"]:
            buf += "\t.{0:<20}({1:<18}){2}\n".format(param,
                                                 module_tags["parameters"][param],
                                                 get_eol(num_params, param_count))
            param_count += 1

        buf += ")%s (\n" % name

    else:
        buf = "%s %s(\n" % (module_tags["module"], name)

    if not wishbone_slave:
        IF_WIRES = []

    #Keep track of the port count so the last one won't have a comma
    port_max = get_port_count(module_tags)
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

    #Add the port declarations
    if "clk" in input_ports:
        buf += "\t.{0:<20}({1:<20}),\n".format("clk", "clk")
    if "rst" in input_ports:
        if invert_reset:
            buf += "\t.{0:<20}({1:<20}),\n".format("rst", "rst_n")
        else:
            buf += "\t.{0:<20}({1:<20}),\n".format("rst", "rst")



    ports = sorted(input_ports, cmp = port_cmp)
    buf += "\n"
    buf += "\t//inputs\n"

    for port in ports:
        port_count += 1
        line = ""
        if port == "rst":
            continue
        if port == "clk":
            continue

        #Check to see if this is one of the pre-defined wires
        wire = ""
        if wishbone_slave:
            for w in IF_WIRES:
                if w.endswith(port[2:]):
                    wire = "%s" % w[2:]
                    break

        #Not Pre-defines
        if len(wire) == 0:
            if len(prename) > 0:
                wire = "%s_%s" % (prename, port)
            else:
                wire = "%s" % port

        line = "\t.{0:<20}({1:<20})".format(port, wire)
        if port_count == port_max:
            buf += "%s\n" % line
        else:
            buf += "%s,\n" % line


    ports = sorted(output_ports, cmp = port_cmp)
    buf += "\n"
    buf += "\t//outputs\n"

    for port in ports:
        port_count += 1
        line = ""
        #Check to see if this is one of the pre-defined wires
        wire = ""
        if wishbone_slave:
            for w in IF_WIRES:
                if w.endswith(port[2:]):
                    wire = "%s" % w[2:]
                    break

        #Not Pre-defines
        if len(wire) == 0:
            if len(prename) > 0:
                wire = "%s_%s" % (prename, port)
            else:
                wire = "%s" % port

        line = "\t.{0:<20}({1:<20})".format(port, wire)
        if port_count == port_max:
            buf += "%s\n" % line
        else:
            buf += "%s,\n" % line

    ports = sorted(inout_ports, cmp = port_cmp)

    if len(ports) > 0:
        buf += "\n"
        buf += "\t//inouts\n"


    for port in ports:
        port_count += 1
        line = ""
        found = False
        #Special Case, we need to tie the specific signal directly to this port
        for key in sorted(slave_tags["bind"], cmp = port_cmp):
            bname = key.partition("[")[0]
            bname.strip()
            if bname == port:
                found = True
                loc = slave_tags["bind"][key]["loc"]
                if port_count == port_max:
                    buf += "\t.{0:<20}({1:<20})\n".format(port, loc)
                else:
                    buf += "\t.{0:<20}({1:<20}),\n".format(port, loc)

        if not found:
            buf += "\t.{0:<20}({1:<20}){2}\n".format(port, port, get_eol(port_max, port_count))


    buf += ");"
    return string.expandtabs(buf, 2)

def get_port_count(module_tags = {}):
    port_count = 0
    if "inout" in module_tags["ports"]:
        port_count += len(module_tags["ports"]["inout"])
    if "output" in module_tags["ports"]:
        port_count += len(module_tags["ports"]["output"])
    if "input" in module_tags["ports"]:
        port_count += len(module_tags["ports"]["input"])
    return port_count



def create_reg_buf_from_dict(name, d):
    size = d["size"]
    if size == 1:
        return create_reg_buf(name, 1, 0, 0)
    else:
        return create_reg_buf(name, size, d["max_val"], d["min_val"])

def create_reg_buf(name, size, max_val, min_val):
    line = ""
    if size > 1:
        size_range = "[%d:%d]" % (max_val, min_val)
        line = "reg\t{0:20}{1};\n".format(size_range, name)
    else:
        line = "reg\t{0:20}{1};\n".format("", name)
    return string.expandtabs(line, 2)



def create_wire_buf_from_dict(name, d):
    size = d["size"]
    if size == 1:
        return create_wire_buf(name, 1, 0, 0)
    else:
        return create_wire_buf(name, size, d["max_val"], d["min_val"])

def create_wire_buf(name, size, max_val, min_val):
    line = ""
    if size > 1:
        size_range = "[%d:%d]" % (max_val, min_val)
        line = "wire\t{0:18}{1};\n".format(size_range, name)
    else:
        line = "wire\t{0:18}{1};\n".format("", name)
    return string.expandtabs(line, 2)

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

def port_cmp(x, y):
    if re.search("[0-9]", x) and re.search("[0-9]", y):
        x_name = x.strip(string.digits)
        y_name = y.strip(string.digits)
        if x_name == y_name:
            #print "%s == %s" % (x_name, y_name)
            x_temp = x.strip(string.letters)
            x_temp = x_temp.strip("[")
            x_temp = x_temp.strip("]")

            y_temp = y.strip(string.letters)
            y_temp = y_temp.strip("[")
            y_temp = y_temp.strip("]")



            x_num = int(x_temp, 10)
            y_num = int(y_temp, 10)
            #print "x:%s, y:%s, x_num:%d, y_num:%d" % (x, y, x_num, y_num)
            if x_num < y_num:
                #print "\tx < y"
                return -1
            if x_num == y_num:
                #print "\tx == y"
                return 0
            if x_num > y_num:
                #print "\tx > y"
                return 1


    #print "normal search: %s:%s" % (x, y)
    if x < y:
        return -1
    if x == y:
        return 0
    else:
        return 1


