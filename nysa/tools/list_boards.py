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

from host.platform_scanner import PlatformScanner

NAME = "boards"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "list available nysa boards (connected/not connected)"

EPILOG = "\n"

white = '\033[0m'
gray = '\033[90m'
red   = '\033[91m'
green = '\033[92m'
yellow = '\033[93m'
blue = '\033[94m'
purple = '\033[95m'
cyan = '\033[96m'

if os.name == "nt":
    white  = ''
    gray   = ''
    red    = ''
    green  = ''
    yellow = ''
    blue   = ''
    purple = ''
    cyan   = ''



def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.add_argument("-r", "--remote", action="store_true", help="Reads all possible Nysa boards available (local and remote)")
    parser.add_argument("-l", "--local", action="store_true", help="Output local boards (connected and not connected)")
    parser.add_argument("-s", "--scan", action="store_true", help="Scan this computer for Nysa boards (Default)")
    return parser

def list_boards(args, status):
    s = status
    pc = PlatformScanner(s)
    pc.get_board_path_dict()
    platform_class_dict = pc.get_platforms()
    for platform in platform_class_dict:
        if s: s.Debug("%s, class: %s" % (platform, str(platform_class_dict[platform])))
        print "Scanning %s%s%s..." % (blue, platform, white),
        p = platform_class_dict[platform](s)
        dev_dict = p.scan()
        if len(dev_dict) > 0:
            print "Found %d board(s)" % len(dev_dict)
            for plat in dev_dict:
                print "\tBoard ID: %s%s%s" % (green, str(plat), white)
        else:
            print "No boards found"

