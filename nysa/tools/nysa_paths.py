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


from nysa.ibuilder.lib import utils
from nysa.ibuilder.lib import xilinx_utils as xutils
from nysa.common import site_manager

NAME = "paths"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "print various paths for different Nysa components"

EPILOG = "\n"


def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.epilog=EPILOG
    parser.add_argument("-v",
                        "--verilog",
                        type = str,
                        nargs = '?',
                        default = "nothing",
                        help = "Return the path to all the verilog modules, or specify a name to get a specific verilog module")
    parser.add_argument("-p",
                        "--platform",
                        type = str,
                        nargs = '?',
                        default = "nothing",
                        help = "Return the path to the board platform directory")
    parser.add_argument("-x",
                        "--xilinx",
                        action = 'store_true',
                        default = False,
                        help = "Returns the path of the default Xilinx source directory")
    parser.add_argument("-u",
                        "--user",
                        action='store_true',
                        default = False,
                        help = "Returns the path of the user project base")
    parser.add_argument("-c",
                        "--cocotb",
                        action='store_true',
                        default = False,
                        help = "Returns the path of Cocotb")
    parser.add_argument("-s",
                        "--silent",
                        action='store_true',
                        default = False,
                        help = "Only return the output, no extra text, this is useful for build tools like 'make'")

    return parser

def nysa_paths(args, status):
    sm = site_manager.SiteManager(status)
    verilog_packages = sm.get_local_verilog_package_names()
    board_packages = sm.get_local_board_names()

    if args.user:
        print_user_project_path(sm, args.silent, status)

    if args.cocotb:
        print_cocotb_path(sm, args.silent, status)

    if args.verilog != "nothing":
        vp = args.verilog
        if vp is None:
            vp = verilog_packages
        elif isinstance(vp, str):
            vp = [vp]
        print_verilog_paths(sm, vp, args.silent, status)

    if args.platform != "nothing":
        bp = args.platform
        if bp is None:
            bp = board_packages
        elif isinstance(bp, str):
            bp = [bp]
        print_platform_paths(sm, bp, args.silent, status)

    if args.xilinx:
        print_xilinx_paths(args.silent, status)

def print_xilinx_paths(silent, status):
    if not silent:
        print "{0:<16}:{1}".format("Xilinx", xutils.find_xilinx_path())
    else:
        print xutils.find_xilinx_path()
    
def print_verilog_paths(sm, names, silent, status):
    for name in names:
        if not silent:
            print "{0:<16}:{1}".format(name, sm.get_local_verilog_package_path(name))
        else:
            print sm.get_local_verilog_package_path(name)

def get_verilog_path(name):
    sm = site_manager.SiteManager()
    return sm.get_local_verilog_package_path(name)

def print_platform_paths(sm, names, silent, status):
    for name in names:
        if not silent:
            print "{0:<16}:{1}".format(name, sm.get_board_directory(name))
        else:
            print sm.get_board_directory(name)

def get_platform_path(name):
    sm = site_manager.SiteManager()
    return sm.get_board_directory(name)

def print_user_project_path(sm, silent, status):
    if not silent:
        print "{0:<16}:{1}".format("User Base Dir", sm.get_nysa_user_base_directory())
    else:
        print sm.get_nysa_user_base_directory()


def print_cocotb_path(sm, silent, status):
    if not silent:
        print "{0:<16}:{1}".format("Cocotb", sm.get_cocotb_directory())
    else:
        print sm.get_cocotb_directory()

