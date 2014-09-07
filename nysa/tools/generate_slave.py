#! /usr/bin/python

#Distributed under the MIT licesnse.
#Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in 
#the Software without restriction, including without limitation the rights to 
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
#of the Software, and to permit persons to whom the Software is furnished to do 
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all 
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
#SOFTWARE.


import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))


from cbuilder.drt import drt
from cbuilder.scripts.cbuilder_factory import CBuilderFactory

EXAMPLE_DIR = os.path.join("home", "user", "Projects", "cbuilder_projects", "project1")
NAME = "generate-slave"
SCRIPT_NAME = "name %s" % NAME
LOCAL_DIR = os.path.abspath(".")

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "\n" \
"Create Nysa Slave Projects\n"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"Generate a Wishbone slave project in the current directory\n" + \
"\tID of 0x01 (GPIO)\n" + \
"\n" + \
"\t\t%s --slaveid 1 <name>\n" % SCRIPT_NAME + \
"\n" + \
"Generate a Wishbone slave project with a sub id number in a specified directory\n" + \
"\tID of 0x02 (UART)\n" + \
"\tSub ID of 0x02\n" + \
"\tOutput Directory: %s\n" % EXAMPLE_DIR + \
"\n" + \
"\t\t%s --slaveid 2 --subid 2 --output %s <name>\n" % (SCRIPT_NAME, EXAMPLE_DIR)+ \
"\n" + \
"Generate a Wishbone slave project with a specified DRT flags\n" + \
"\tID of 0x02 (UART)\n" + \
"\tFlags of 0x01 = 'Standard Device'\n" + \
"\n" + \
"\t\t%s --slaveid 2 --flags 1 <name>\n" % SCRIPT_NAME+ \
"\n" + \
"Generate a Wishbone memory slave project\n" + \
"\n" + \
"\t\t%s --memory <name>\n" % SCRIPT_NAME + \
"\n" + \
"Generate an Axi slave project\n" + \
"\tID of 0x04 (SPI)\n" + \
"\n" + \
"\t\t%s --axi --slaveid 4 <name>\n" % SCRIPT_NAME + \
"\n"


def print_device_list():
    dev_list = drt.get_device_list()
    print "Available Devices:"
    for dev in dev_list:
        print "%s" % str(dev)

def setup_parser(parser):
    parser.description = DESCRIPTION
    #Add an argument to the parser
    #Optional
    parser.add_argument("--axi",
                        action='store_true',
                        default = False,
                        help = "Set the bus type as AXI (Wishbone by default)")
    parser.add_argument("--memory",
                        action='store_true',
                        default = False,
                        help = "Generate a memory slave core")
    parser.add_argument("--slaveid",
                        type = str,
                        nargs=1,
                        default=None,
                        help="Specify the slave identification number, use \"nysa-device-list\" to view a list of possible device IDs")
    parser.add_argument("--subid",
                        type=str,
                        nargs=1,
                        default="0",
                        help = "Specify the sub ID number, used to identify a unique version of a device Example: a unique GPIO that uses internal PWMs would have a unique Sub ID to differentiate itself from other GPIO devices")
    parser.add_argument("--flags",
                        type=str,
                        nargs=1,
                        default="1",
                        help = "Specify default flags that should be put into the module, these can be overriden in the module by overwritting the DRT_FLAGS metavariable")
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
    '''
    parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
      description=DESCRIPTION,
      epilog=EPILOG
    )
 
    debug = False
    cb = {}
    cb["name"] = None
    cb["drt_id"] = 0
    cb["drt_sub_id"] = 0
    cb["drt_size"] = 0
    cb["drt_flags"] = 1
    cb["bus_type"] = "slave"
    cb["type"] = "wishbone"
    cb["subtype"] = "peripheral"
    cb["base"] = os.path.abspath(os.path.dirname(__file__))

    #Add an argument to the parser
    #Optional
    parser.add_argument("-d",
                        "--debug",
                        action='store_true',
                        help="Output test debug information")
    parser.add_argument("--axi",
                        action='store_true',
                        default = False,
                        help = "Set the bus type as AXI (Wishbone by default)")
    parser.add_argument("--memory",
                        action='store_true',
                        default = False,
                        help = "Generate a memory slave core")
    parser.add_argument("--slaveid",
                        type = str,
                        nargs=1,
                        default=None,
                        help="Specify the slave identification number, use \"nysa-device-list\" to view a list of possible device IDs")
    parser.add_argument("--subid",
                        type=str,
                        nargs=1,
                        default="0",
                        help = "Specify the sub ID number, used to identify a unique version of a device Example: a unique GPIO that uses internal PWMs would have a unique Sub ID to differentiate itself from other GPIO devices")
    parser.add_argument("--flags",
                        type=str,
                        nargs=1,
                        default="1",
                        help = "Specify default flags that should be put into the module, these can be overriden in the module by overwritting the DRT_FLAGS metavariable")
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
    parser.parse_args()
    args = parser.parse_args()
    '''
    value = 0
    cb = {}
    cb["name"] = None
    cb["drt_id"] = 0
    cb["drt_sub_id"] = 0
    cb["drt_size"] = 0
    cb["drt_flags"] = 1
    cb["bus_type"] = "slave"
    cb["type"] = "wishbone"
    cb["subtype"] = "peripheral"
    cb["base"] = os.path.abspath(os.path.dirname(__file__))



    #Parse the command line arguments
    if args.debug:
        print "Debug Enable"
        debug = True
    
    if args.slaveid is None and not args.memory:
        print "Error: No slave ID is given and a memory device was not specified, either a slave ID must be specified or the memory flag must be set"
        args.print_help()
        sys.exit(-1)

    if args.slaveid is not None and args.memory:
        print "Error: Slave ID and Memory Cannot be specified at the same time"
        #print "args: %s" % str(dir(args))
        #args.print_help()
        sys.exit(-2)

    if args.memory:
        #Memory Device
        if debug: "Memory Device"
        cb["drt_id"] = 5
        cb["subtype"] = "memory"
 
    else:
        value = args.slaveid[0]
        if value.isdigit():
            value = int(value, 10)
        else:
            value = int(value, 16)
        if debug: print "Value: 0x%02X" % value

    if args.axi:
        if debug: print "Axi Bus"
        cb["type"] = "axi"
    else:
        cb["type"] = "wishbone"
        if debug: print "Wishbone Bus"

    cb["base"] = args.output[0]
    if debug: print "Output directory: %s" % str(cb["base"])

    cb["name"] = args.name[0]

    cbuilder = CBuilderFactory(cb)


