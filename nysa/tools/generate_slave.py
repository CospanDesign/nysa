#! /usr/bin/python

# Distributed under the MIT license.
# Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sys
import os
import time
import shutil
import glob

from string import Template

from nysa.cbuilder.sdb import SDBError
from device_list import get_num_from_name
from nysa.cbuilder import device_manager as dm

EXAMPLE_DIR = os.path.join("home", "user", "Projects", "cbuilder_projects", "project1")
NAME = "generate-slave"
SCRIPT_NAME = "name %s" % NAME
LOCAL_DIR = os.getcwd()

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "create a project to generate a nysa compatible core"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"Generate a Wishbone slave project in the current directory\n" + \
"\tID of 0x02 (GPIO)\n" + \
"\n" + \
"\t\t%s --major 2 <name>\n" % SCRIPT_NAME + \
"\n" + \
"Generate a Wishbone slave project with a sub id number in a specified directory\n" + \
"\tID of 0x03 (UART)\n" + \
"\tSub ID of 0x02\n" + \
"\tOutput Directory: %s\n" % EXAMPLE_DIR + \
"\n" + \
"\t\t%s --major 3 --minor 2 --output %s <name>\n" % (SCRIPT_NAME, EXAMPLE_DIR)+ \
"\n" + \
"Generate an Axi slave project (NOT IMPLEMENTED YET!)\n" + \
"\tID of 0x05 (SPI)\n" + \
"\n" + \
"\t\t%s --axi --major 5 <name>\n" % SCRIPT_NAME + \
"\n" + \
"Add the Cocotb build tools to the project\n" + \
"\t\t%s -c <name>\n" % SCRIPT_NAME + \
"\n"

def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.epilog=EPILOG
    ed = "0x%02X" % get_num_from_name("experiment")
    #print "ed: %s" % ed
    #Add an argument to the parser
    #Optional
    parser.add_argument("--axi",
                        action='store_true',
                        default = False,
                        help = "Set the bus type as AXI (Wishbone by default)")
    parser.add_argument("--major",
                        type = str,
                        nargs=1,
                        default=[ed],
                        help="Specify the slave identification number (hex), use \"nysa device\" command to view a list of possible device IDs")
    parser.add_argument("--minor",
                        type=str,
                        nargs=1,
                        default="0",
                        help = "Specify the sub ID number (hex), used to identify a unique version of a device Example: a unique GPIO that uses internal PWMs would have a unique Sub ID to differentiate itself from other GPIO devices")
    parser.add_argument("-o",
                        "--output",
                        type = str,
                        nargs=1,
                        default=[LOCAL_DIR],
                        help="Specify a location for the generated project, defaults to current directory")
    parser.add_argument("-c",
                        "--cocotb",
                        action = "store_true",
                        help = "Add Cocotb simulation directory to project")
    #Required
    parser.add_argument("name",
                        type = str,
                        nargs=1,
                        default=None,
                        help="Specify the name of the project file")

    return parser

def generate_slave(args, status):

    debug = False
    value = 0
    if args.axi:
        raise SDBError("AXI Slave Generator not implemented yet")


    #Parse the command line arguments
    if args.debug:
        print "Debug Enable"
        debug = True

    #XXX: Not really useful now but in the future when we use AXI this will come in handy
    wishbone_bus = True
    output_path = os.path.expanduser(args.output[0])

    slave_dict = {}
    slave_dict["NAME"] = args.name[0]
    slave_dict["ABI_MAJOR"] = args.major[0]
    slave_dict["ABI_MINOR"] = args.minor[0]

    generate_slave_from_dict(slave_dict, output_path, status)
    if args.cocotb:
        output_dir = os.path.join(output_path, args.name[0])
        add_cocotb(slave_dict, output_dir, status)

def generate_slave_from_dict(slave_dict, output_path, status):
    if "VENDOR_ID" not in slave_dict:
        slave_dict["VENDOR_ID"] = "0x800000000000C594"
    if "DEVICE_ID" not in slave_dict:
        slave_dict["DEVICE_ID"] = "0x800000000000C594"
    if "ABI_CLASS" not in slave_dict:
        slave_dict["ABI_CLASS"] = "0"
    if "CORE_VERSION" not in slave_dict:
        slave_dict["CORE_VERSION"] = "00.000.001"
    if "URL" not in slave_dict:
        slave_dict["URL"] = "http://www.example.com"
    if "DATE" not in slave_dict:
        slave_dict["DATE"] = time.strftime("%Y/%m/%d")
    if "EXECUTABLE" not in slave_dict:
        slave_dict["EXECUTABLE"] = "True"
    if "WRITEABLE" not in slave_dict:
        slave_dict["WRITEABLE"] = "True"
    if "READABLE" not in slave_dict:
        slave_dict["READABLE"] = "True"
    if "SIZE" not in slave_dict:
        slave_dict["SIZE"] = "3"

    name = slave_dict["NAME"]

    #Get a reference to the template directory
    template_path = os.path.join(os.path.dirname(__file__),
                                 os.pardir,
                                 "data",
                                 "template",
                                 "wishbone")
    template_path = os.path.abspath(template_path)

    #Create the output directory
    output_dir = os.path.join(output_path, name)

    generate_directory_structure(template_path, output_dir)

    #Get a reference to the template slave file
    f = open(os.path.join(template_path, "rtl", "USER_SLAVE.v"), 'r')
    template = Template(f.read())
    f.close()

    #Substitute all values we got from the user
    slave_buffer = template.safe_substitute(
        SDB_VENDOR_ID           = slave_dict["VENDOR_ID"],
        SDB_DEVICE_ID           = slave_dict["DEVICE_ID"],
        SDB_CORE_VERSION        = slave_dict["CORE_VERSION"],
        SDB_NAME                = slave_dict["NAME"],
        SDB_ABI_CLASS           = slave_dict["ABI_CLASS"],
        SDB_ABI_VERSION_MAJOR   = slave_dict["ABI_MAJOR"],
        SDB_ABI_VERSION_MINOR   = slave_dict["ABI_MINOR"],
        SDB_MODULE_URL          = slave_dict["URL"],
        SDB_DATE                = slave_dict["DATE"],
        SDB_EXECUTABLE          = slave_dict["EXECUTABLE"],
        SDB_WRITEABLE           = slave_dict["WRITEABLE"],
        SDB_READABLE            = slave_dict["READABLE"],
        SDB_SIZE                = slave_dict["SIZE"]
    )
    #print "slave buffer:"
    #print slave_buffer

    #Get a reference to the output slave
    f = open(os.path.join(output_dir, "rtl", name + ".v"), 'w')
    f.write(slave_buffer)
    f.close()

    #Process the test bench
    f = open(os.path.join(template_path, "sim", "tb_wishbone_master.v"), 'r')
    template = Template(f.read())
    f.close()

    #Substitute name
    tb_buffer = template.safe_substitute(
        SDB_NAME                = name
    )
    f = open(os.path.join(output_dir, "sim", "tb_wishbone_master.v"), 'w')
    f.write(tb_buffer)
    f.close()

    #Process the command file
    f = open(os.path.join(template_path, "command_file.txt"), 'r')
    template = Template(f.read())
    f.close()

    c_buffer = template.safe_substitute(
        SDB_NAME                = name
    )

    f = open(os.path.join(output_dir, "command_file.txt"), 'w')
    f.write(c_buffer)
    f.close()

    #Copy the rest of the slave files to the new directory
    file_list = generate_file_list(template_path)
    #print "files: %s" % str(file_list)

    #The rest of the files are just boilerplate copy the files
    for filename in file_list:
        #print "filename: %s" % str(filename)
        if os.path.split(filename)[-1] == "USER_SLAVE.v":
            continue
        if os.path.split(filename)[-1] == "command_file.txt":
            continue
        if os.path.split(filename)[-1] == "tb_wishbone_master.v":
            continue

        source_path = os.path.join(template_path, filename)
        dest_path = os.path.join(output_dir, filename)
        shutil.copy(source_path, dest_path)

def add_cocotb(slave_dict, output_path, status):
    status.Debug("Adding COCOTB to Project")
    cocotb_spath = os.path.join(os.path.dirname(__file__),
                                 os.pardir,
                                 "data",
                                 "template",
                                 "cocotb")
    cocotb_spath = os.path.abspath(cocotb_spath)
    cocotb_dpath = os.path.join(output_path, "cocotb")
    status.Debug("output: %s" % cocotb_dpath)
    file_list = generate_file_list(cocotb_spath)
    if not os.path.exists(cocotb_dpath):
        os.makedirs(cocotb_dpath)
    fl = []
    #for f in file_list:
    #    p = os.path.join(cocotb_spath, f)
    #    fl.append(p)

    for fn in file_list:
        source_file = os.path.join(cocotb_spath, fn)
        dest_file   = os.path.join(cocotb_dpath, fn)
        status.Debug("reading: %s" % source_file)
        f = open(source_file, 'r') 
        template = Template(f.read())
        f.close()
        v = int(slave_dict["ABI_MAJOR"], 0)
        device_name = str(dm.get_device_name_from_id(v))
        buf = template.safe_substitute(
            SDB_VENDOR_ID           = slave_dict["VENDOR_ID"],
            SDB_DEVICE_ID           = slave_dict["DEVICE_ID"],
            SDB_CORE_VERSION        = slave_dict["CORE_VERSION"],
            SDB_NAME                = slave_dict["NAME"],
            SDB_ABI_CLASS           = slave_dict["ABI_CLASS"],
            SDB_ABI_VERSION_MAJOR   = slave_dict["ABI_MAJOR"],
            SDB_ABI_VERSION_MINOR   = slave_dict["ABI_MINOR"],
            SDB_MODULE_URL          = slave_dict["URL"],
            SDB_DATE                = slave_dict["DATE"],
            SDB_EXECUTABLE          = slave_dict["EXECUTABLE"],
            SDB_WRITEABLE           = slave_dict["WRITEABLE"],
            SDB_READABLE            = slave_dict["READABLE"],
            SDB_SIZE                = slave_dict["SIZE"],
            DEVICE_NAME             = device_name
        )
        status.Debug("writing: %s" % dest_file)
        f = open(dest_file, "w")
        f.write(buf)
        f.close()

def generate_file_list(template_path):
    #Copy the rest of the slave files to the new directory
    file_list_in = []
    for root, dirs, files in os.walk(template_path):
        for f in files:
            file_list_in.append(os.path.join(root, f))

    file_list = []

    for f in file_list_in:
        file_list.append(f.partition(template_path)[2][1:])

    return file_list

def generate_directory_structure(template_path, output_path):
    for f in generate_file_list(template_path):
        if len(os.path.split(f)) > 1 and os.path.split(f)[0] != "":
            path_list = os.path.split(f)[:-1]
            dir_path = path_list[0]
            for p in path_list[1:]:
                dir_path = os.path.join(p)
            generated_dir = os.path.join(output_path, dir_path)
            if os.path.exists(generated_dir):
                continue
            else:
                try:
                    #print "Generating: %s" % generated_dir
                    os.makedirs(generated_dir)
                except OSError as err:
                    pass
