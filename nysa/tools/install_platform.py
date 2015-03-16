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
import subprocess

from nysa.common import site_manager
from nysa.common import status as sts

NAME = "install-platform"
SCRIPT_NAME = "nysa %s" % NAME


__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "Install a platform to the local system"
EPILOG = "Install a platform to a local system\n" + \
"if no platform is specified the remote platforms are listed\n" + \
"if 'all' is specified then all platforms available will be\n" + \
"downloaded and installed\n" + \
"\n"

def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.epilog = EPILOG
    parser.add_argument("name",
                        type = str,
                        nargs = '?',
                        default = "list",
                        help = "Specify what to install")
    return parser

def install(args, status):
    s = status
    sm = site_manager.SiteManager(status)
    names = []

    if s: s.Verbose("Args: %s" % str(args))

    board_dict = sm.get_remote_board_dict()

    if args.name == "list":
        if s:s.Info("Get a list of the remote platforms")

        print "%sPlatforms:%s" % (sts.purple, sts.white)
        for platform in board_dict:
            print "\t%s%s%s" % (sts.blue, platform, sts.white)
            print "\t\t%sAdded: %s%s" % (sts.green, board_dict[platform]["timestamp"], sts.white)
            print "\t\t%sRepo: %s%s" % (sts.green, board_dict[platform]["repository"], sts.white)
            print "\t\t%sPIP: %s%s" % (sts.green, board_dict[platform]["pip"], sts.white)

        sys.exit(0)

    if args.name == "all":
        if s:s.Info("Install all platforms")
        names = board_dict.keys()
    else:
        names = [args.name]


    print "%sInstalling platforms:%s " % (sts.purple, sts.white),
    for name in names:
        print "\t%s%s%s" % (sts.blue, name, sts.white)
        if len(board_dict[name]["pip"]) == 0:
            board_dict[name]["pip"] = "git+" + board_dict[name]["repository"] + ".git"
        print "\t%sInstalling from URL: %s%s" % (sts.blue, board_dict[name]["pip"], sts.white)
        subprocess.call(["sudo", "pip", "install", "--upgrade", board_dict[name]["pip"]])

