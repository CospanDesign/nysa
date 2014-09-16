#! /usr/bin/python

#Distributed under the MIT licesnse.
#Copyright (c) 2014 Dave McCoy (dave.mccoy@cospandesign.com)

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
import zipfile
import shutil
import collections


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
from common import status
import image_builder
import nysa_utils
import device_list
import generate_slave
import list_boards
import reset_board
import program_board
import upload_board
import list_platforms
import drt_viewer
import init
import install_platform
import nysa_status

from completer_extractor import completer_extractor as ce

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

SCRIPT_NAME = os.path.basename(__file__)

DESCRIPTION = "Nysa Tool"


COMPLETER_EXTRACTOR = False
TEMP_BASH_COMPLETER_FILEPATH = "nsya"

EPILOG = "Enter the toolname with a -h to find help about that specific tool\n"

TYPE_DICT = collections.OrderedDict()
TYPE_DICT["cbuilder"] = "Functions to help create code to go into platforms"
TYPE_DICT["ibuilder"] = "Functions to generate an entire image (or binary) to be downloaded into a platform"
TYPE_DICT["host"] = "Functions to view and control boards"
TYPE_DICT["utility"] = "Functions to update and/or upgrade the nysa tool including adding new platforms and verilog packages"

TOOL_DICT = {
    generate_slave.NAME:{
        "type":"cbuilder",
        "module":generate_slave,
        "tool":generate_slave.generate_slave
    },
    image_builder.NAME:{
        "type":"ibuilder",
        "module":image_builder,
        "tool":image_builder.image_builder
    },
    nysa_utils.NAME:{
        "type":"utility",
        "module":nysa_utils,
        "tool":nysa_utils.nysa_utils
    },
    reset_board.NAME:{
        "type":"host",
        "module":reset_board,
        "tool":reset_board.reset_board
    },
    program_board.NAME:{
        "type":"host",
        "module":program_board,
        "tool":program_board.program_board
    },
    upload_board.NAME:{
        "type":"host",
        "module":upload_board,
        "tool":upload_board.upload_board
    },
    list_platforms.NAME:{
        "type":"utility",
        "module":list_platforms,
        "tool":list_platforms.list_platforms
    },
    list_boards.NAME:{
        "type":"host",
        "module":list_boards,
        "tool":list_boards.list_boards
    },
    device_list.NAME:{
        "type":"cbuilder",
        "module":device_list,
        "tool":device_list.device_list
    },
    drt_viewer.NAME:{
        "type":"host",
        "module":drt_viewer,
        "tool":drt_viewer.view_drt
    },
    init.NAME:{
        "type":"utility",
        "module":init,
        "tool":init.init
    },
    install_platform.NAME:{
        "type":"utility",
        "module":install_platform,
        "tool":install_platform.install
    },
    nysa_status.NAME:{
        "type":"utility",
        "module":nysa_status,
        "tool":nysa_status.nysa_status
    }
}


def update_epilog():
    global EPILOG
    tool_type_dict = collections.OrderedDict()
    for type_d in TYPE_DICT:
        tool_type_dict[type_d] = {}
        tool_type_dict[type_d]["description"] = TYPE_DICT[type_d]
        tool_type_dict[type_d]["tools"] = []

    for tool in TOOL_DICT:
        
        tool_type_dict[TOOL_DICT[tool]["type"]]["tools"].append(tool)

    EPILOG += "\n"
    EPILOG += "Tools:\n\n"
    for tool_type in tool_type_dict:
        EPILOG += "{0:25}{1}\n\n".format(tool_type, tool_type_dict[tool_type]["description"])
        for tool in tool_type_dict[tool_type]["tools"]:
            EPILOG += "{0:5}{1:20}{2}\n".format("", tool, TOOL_DICT[tool]["module"].DESCRIPTION)
        EPILOG += "\n"
        

    EPILOG += "\n"


def main():
    update_epilog()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    #Setup the status message
    s = status.Status()
    s.set_level(status.StatusLevel.INFO)

    #Global Flags
    parser.add_argument("-v", "--verbose", action='store_true', help="Output verbose information")
    parser.add_argument("-d", "--debug", action='store_true', help="Output test debug information")


    subparsers = parser.add_subparsers( title = "Tools",
                                        description = "Nysa Tools",
                                        metavar = None,
                                        dest = "tool")

    for tool in TOOL_DICT:
        p = subparsers.add_parser(tool,
                                  description=TOOL_DICT[tool]["module"].DESCRIPTION,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
        TOOL_DICT[tool]["module"].setup_parser(p)
        TOOL_DICT[tool]["parser"] = p


    #Parse the arguments
    if COMPLETER_EXTRACTOR:
        ce(parser, TEMP_BASH_COMPLETER_FILEPATH)
        return
        
    args = parser.parse_args()

    if args.debug:
        s.set_level(status.StatusLevel.DEBUG)

    if args.verbose:
        s.set_level(status.StatusLevel.VERBOSE)

    #print "args: %s" % str(args)
    #print "args dict: %s" % str(dir(args))
    TOOL_DICT[args.tool]["tool"](args, s)

