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


SCRIPT_NAME = os.path.basename(__file__)

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "Board level control (Program/Reset/Upload)"

EPILOG = "\n" \
"Examples:\n" + \
"Reset the board\n" + \
"\tnysa %s <board_name> [--serial Serial Number] -r\n" % SCRIPT_NAME + \
"\n"

def setup_parser(parser):
    parser.add_argument("command", type=str, nargs=1, default="list", help="Command to be performed")
    parser.add_argument("board", type=str, nargs='?', default="", help="Target board")
    parser.add_argument("-s", "--serial", type = str, nargs=1, default="", help="Specify the serial number of a board")
    subparsers = parser.add_subparsers(title = "Board Tools",
                                       description = "Board Level Tools",
                                       dest = "tool")

    list_parser = subparsers.add_parser("list", description = "list possible Nysa boards")
    list_parser.add_argument("-r", "--remote", action="store_true", help="Output remote board info")

    return parser

def board_control(args, status):
    s = status
