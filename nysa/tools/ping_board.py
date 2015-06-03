# Distributed under the MIT licesnse.
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
import time

from nysa.host.platform_scanner import find_board
from nysa.host.platform_scanner import PlatformScannerException

NAME = "ping"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "performs a board ping, this is the simplest level of communication\n" \
              "If a board responds to a ping it has been reset and the clock is running correctly"

EPILOG = "\n"


def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.add_argument("name",
                        type=str,
                        nargs='?',
                        default="any",
                        help="Specify a board to ping, if there is only one board attached leave blank (ignoring SIM)")

    parser.add_argument("-s", "--serial",
                        type=str,
                        nargs=1,
                        help="Specify the serial number or unique ID of the board")

    return parser


def ping_board(args, status):
    s = status
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

    board.ping()
