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

from nysa.cbuilder.sdb import SDB
from nysa.cbuilder.sdb import SDBError

EXAMPLE_DIR = os.path.join("home", "user", "Projects", "cbuilder_projects", "project1")
NAME = "generate-slave"
SCRIPT_NAME = "name %s" % NAME
LOCAL_DIR = os.path.abspath(".")

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "Create a project to generate a nysa compatible core"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"Generate a Wishbone slave project in the current directory\n" + \
"\tID of 0x01 (GPIO)\n" + \
"\n" + \
"\t\t%s --major 1 <name>\n" % SCRIPT_NAME + \
"\n" + \
"Generate a Wishbone slave project with a sub id number in a specified directory\n" + \
"\tID of 0x02 (UART)\n" + \
"\tSub ID of 0x02\n" + \
"\tOutput Directory: %s\n" % EXAMPLE_DIR + \
"\n" + \
"\t\t%s --major 2 --minor 2 --output %s <name>\n" % (SCRIPT_NAME, EXAMPLE_DIR)+ \
"\n" + \
"Generate a Wishbone slave project with a specified DRT flags\n" + \
"\tID of 0x02 (UART)\n" + \
"\tFlags of 0x01 = 'Standard Device'\n" + \
"\n" + \
"\t\t%s --major 2 --flags 1 <name>\n" % SCRIPT_NAME+ \
"\n" + \
"Generate a Wishbone memory slave project\n" + \
"\n" + \
"\t\t%s --memory <name>\n" % SCRIPT_NAME + \
"\n" + \
"Generate an Axi slave project\n" + \
"\tID of 0x04 (SPI)\n" + \
"\n" + \
"\t\t%s --axi --major 4 <name>\n" % SCRIPT_NAME + \
"\n"

def print_device_list():
    dev_list = sdb.get_device_list()
    print "Available Devices:"
    for dev in dev_list:
        print "%s" % str(dev)

def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.epilog=EPILOG
    #Add an argument to the parser
    #Optional
    parser.add_argument("--axi",
                        action='store_true',
                        default = False,
                        help = "Set the bus type as AXI (Wishbone by default)")
    parser.add_argument("--major",
                        type = str,
                        nargs=1,
                        default="0",
                        help="Specify the slave identification number (hex), use \"nysa-device-list\" to view a list of possible device IDs")
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

    #Get a reference to the template directory
    template_path = os.path.join(os.path.dirname(__file__),
                                 os.pardir,
                                 "data",
                                 "template",
                                 "wishbone")
    template_path = os.path.abspath(template_path)

    #Create the output directory
    output_dir = os.path.join(args.output, args.name)

    generate_directory_structure(template_path, output_dir)

    #Get a reference to the template slave file
    f = open(os.path.join(template_path, "rtl", "USER_SLAVE.v"), 'r')
    template = Template(f.read())
    f.close()

    #Substitute all values we got from the user
    slave_buffer = template.safe_substitute(
        SDB_VENDOR_ID           = "0x800000000000C594",
        SDB_DEVICE_ID           = "0x00000000",
        SDB_CORE_VERSION        = "00.000.001",
        SDB_NAME                = args.name,
        SDB_ABI_CLASS           = "0",
        SDB_ABI_VERSION_MAJOR   = args.major,
        SDB_ABI_VERSION_MINOR   = args.minor,
        SDB_MODULE_URL          = "http://www.example.com",
        SDB_DATE                = time.strftime("%Y/%m/%d"),
        SDB_EXECUTABLE          = "True",
        SDB_WRITEABLE           = "True",
        SDB_READABLE            = "True",
        SDB_SIZE                = "3"
    )
    #print "slave buffer:"
    #print slave_buffer

    #Get a reference to the output slave
    f = open(os.path.join(output_dir, "rtl", args.name + ".v"), 'w')
    f.write(slave_buffer)
    f.close()

    #Process the test bench
    f = open(os.path.join(template_path, "sim", "tb_wishbone_master.v"), 'r')
    template = Template(f.read())
    f.close()

    #Substitute name
    tb_buffer = template.safe_substitute(
        SDB_NAME                = args.name
    )
    f = open(os.path.join(output_dir, "sim", "tb_wishbone_master.v"), 'w')
    f.write(tb_buffer)
    f.close()

    #Process the command file
    f = open(os.path.join(template_path, "command_file.txt"), 'r')
    template = Template(f.read())
    f.close()

    c_buffer = template.safe_substitute(
        SDB_NAME                = args.name
    )

    f = open(os.path.join(output_dir, "command_file.txt"), 'w')
    f.write(c_buffer)
    f.close()

    #Copy the rest of the slave files to the new directory
    file_list = generate_file_list(template_path)
    print "files: %s" % str(file_list)

    #The rest of the files are just boilerplate copy the files
    for filename in file_list:
        print "filename: %s" % str(filename)
        if os.path.split(filename)[-1] == "USER_SLAVE.v":
            continue
        if os.path.split(filename)[-1] == "command_file.txt":
            continue
        if os.path.split(filename)[-1] == "tb_wishbone_master.v":
            continue

        source_path = os.path.join(template_path, filename)
        dest_path = os.path.join(output_dir, filename)
        shutil.copy(source_path, dest_path)

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
                    print "Generating: %s" % generated_dir
                    os.makedirs(generated_dir)
                except OSError as err:
                    pass
