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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from host.platform_scanner import find_board
from host.platform_scanner import PlatformScanner
from host.platform_scanner import PlatformScannerException

NAME = "upload"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "Upload a program file to the specified board"

EPILOG = "If there is only one board attached, then it will be assumed otherwise a name and or serial\/board id might be required\n"

def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.epilog = EPILOG

    parser.add_argument("bin",
                        type = str,
                        nargs = 1,
                        help = "Binary file to upload")

    parser.add_argument("name",
                        type = str,
                        nargs = '?',
                        default = "any",
                        help = "Specify a board to initiate a upload, if there is only one board attached leave blank (ignoring SIM)")
    parser.add_argument("-s", "--serial",
                        type = str,
                        nargs = 1,
                        help = "Specify the serial number or unique ID of the board")

    return parser

def upload_board(args, status):
    s = status
    #print "args.name: %s" % args.name
    name = args.name
    if name == "any":
        name = None
    serial = None
    board = None
    if args.serial is not None:
        serial = args.serial[0]

    try:    
        board = find_board(name, serial, status)
    except PlatformScannerException as ex:
        if s: s.Error("%s" % str(ex))
        sys.exit(1)

    board.upload(args.bin[0])
    board.program()

def upload(board_name, serial_number, file_path, status):
    board = find_board(board_name, serial_number, status)
    board.upload(file_path)
    board.program()

