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

import subprocess

from nysa.ibuilder import utils

from nysa.host.platform_scanner import PlatformScanner

from nysa.common import site_manager
from nysa.common import status as st

NAME = "status"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "print the status of the nysa tools"

EPILOG = "\n"

INTERNET_AVAILABLE = False

def setup_parser(parser):
    parser.description = DESCRIPTION
    return parser


def cbuilder_status(status):
    s = status
    sm = site_manager.SiteManager(status)
    verilog_packages = sm.get_local_verilog_package_names()
    print "%scbuilder:%s" % (st.yellow, st.white)

    if not INTERNET_AVAILABLE:
        print "\tInternet not available, unable to check for remote verilog repositories"
    else:
        vdict = sm.get_remote_verilog_dict()
        print "\t%sRemote Verilog Modules Available%s" % (st.purple, st.white)
        for name in vdict:
            print "\t\t%s%s%s" % (st.blue, name, st.white)

    print "\t%sInstalled Verilog Modules%s" % (st.purple, st.white)
    for vp in verilog_packages:
        print "\t\t%s%s%s" % (st.blue, vp, st.white)

    print ""
    print "\tchecking for iverilog...",
    result = subprocess.call(["iverilog", "-V"], stdout = subprocess.PIPE)
    #print "Result: %s" % str(type(result))
    if result == 0:
        print "%sFound!%s" % (st.green, st.white)
    else:
        print "%sNot Found!%s" % (st.red, st.white)

    print "\tchecking for gtkwave...",
    result = subprocess.call(["gtkwave", "-V"], stdout = subprocess.PIPE)
    if result == 0:
        print "%sFound!%s" % (st.green, st.white)
    else:
        print "%sNot Found!%s" % (st.red, st.white)

    print ""

def ibuilder_status(status):
    s = status
    print "%sibuilder:%s" % (st.yellow, st.white)

    if not INTERNET_AVAILABLE:
        print "\tInternet not available, unable to check for remote platform packages"
    else:
        sm = site_manager.SiteManager(status)
        board_dict = sm.get_remote_board_dict()
        print "\t%sRemote Platform Packages Available:%s" % (st.purple, st.white)
        for name in board_dict:
            print "\t\t%s%s%s" % (st.blue, name, st.white)

    #print "args.name: %s" % args.name
    ps = PlatformScanner(s)
    platforms = ps.get_platforms()
    if len(platforms) == 0:
        print "\t%sNo Platforms installed!%s" % (st.red, st.white)
        print "\t\tuse %s'nysa install-platforms'%s to view all available remote platforms" % (st.blue, st.white)
        print "\t\tuse %s'nysa install-platforms <platform name>'%s to install a platform" % (st.green, st.white)
    else:
        print "\t%sPlatforms:%s" % (st.purple, st.white)
        for platform in platforms:
            print "\t\t%s%s%s" % (st.blue, platform, st.white)
            p = ps.get_platforms()[platform](status)
            print "\t\t\tChecking build tool...",
            if not p.test_build_tools():
                print "%s%s%s" % (st.red, "Failed!", st.white)
            else:
                print "%s%s%s" % (st.green, "Passed!", st.white)

    print ""

def host_status(status):
    s = status
    print "%shost controller:%s" % (st.yellow, st.white)
    print ""

def nysa_status(args, status):
    global INTERNET_AVAILABLE
    INTERNET_AVAILABLE = utils.try_internet()

    cbuilder_status(status)
    ibuilder_status(status)
    host_status(status)

