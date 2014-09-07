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
import json
import site

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from ibuilder.lib import utils

NAME = "status"
SCRIPT_NAME = "nysa %s" % NAME
DESCRIPTION = "Check for available boards and verilog"

def setup_parser(parser):
    parser.description = DESCRIPTION
    return parser

def check(args, status):
    s = status
    s.Important("Cleaning up verilog paths")
    utils.clean_verilog_package_paths()
    utils.update_verilog_package("nysa-verilog")
    s.Important("Updated %s, located at: %s" % ("nysa-verilog", utils.get_local_verilog_path("nysa-verilog")))

