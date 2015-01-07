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

from nysa.cbuilder import device_manager as dm

NAME = "devices"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "Manage/View devices IDs and descriptions"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"Print the device number given the string name\n" + \
"\t%s -n gpio\n" % (SCRIPT_NAME) + \
"\n" + \
"Returns the device number as the return status\n" + \
"\t%s -i gpio\n" % (SCRIPT_NAME) + \
"\t\tHow to use: %s -i gpio ; echo$?\n" % (SCRIPT_NAME)
#"View Devices:\n" + \
#"\t%s -l\n" % (SCRIPT_NAME) + \
#"\n" + \
#"Debug data:\n" + \
#"\t%s -d\n" % (SCRIPT_NAME) + \

def print_device_list():
    print "Getting device list"
    dev_list = dm.get_device_list()
    print "Available Devices:"
    for dev in dev_list:
        if int(dev["ID"], 16) == 0:
            continue

        #print "%s (0x%02X): %s" % (dev["name"], int(dev["ID"], 16), dev["description"])
        print "{0:20} 0x{1:0=2X} : {2}".format(dev["name"], int(dev["ID"], 16), dev["description"])

def get_num_from_name(name):
    dev_list = dm.get_device_list()
    for dev in dev_list:
        if dev["name"].lower() == name.lower():
            return int(dev["ID"], 16)

    return None

def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.add_argument("-d", "--debug", action='store_true', help="Output test debug information")
    parser.add_argument("-n", "--name", type = str, nargs=1, default="", help = "Specify a device name to get the device number (Returns hex string)")
    parser.add_argument("-i", "--integer", type = str, nargs=1, default="", help = "Specify a device name to get the device number (Returns number)")
    return parser

def device_list(args, status):
    s = status

    if args.name is not "":
        if s: s.Info("Got Name (String): %s" % args.name[0])
        index = get_num_from_name(args.name[0])
        if s: s.Info("\t0x%02X" % index)
        sys.exit(0)

    elif args.integer is not "":
        if s: s.Info("Got Name (Integer): %s" % args.integer[0])
        index = get_num_from_name(args.integer[0])
        sys.exit(index)

    print_device_list()


