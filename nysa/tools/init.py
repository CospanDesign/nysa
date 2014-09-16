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
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from ibuilder.lib import utils
from common import site_manager

NAME = "init"
SCRIPT_NAME = "nysa %s" % NAME


__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "Creates the local nysa_projects directory, initializes the configuration files To see the status of the current nysa setup run 'nysa status'"
EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"Initialize configuration and sets up the base directory at: %s\n" % site_manager.DEFAULT_USER_BASE + \
"\t%s\n" % SCRIPT_NAME + \
"\n" + \
"Initialize configuration and reads the directory from the user\n" + \
"NOTE: This can only be run on an unintialized development platform,\n" + \
"otherwise specify '-F' to force the new directory\n" + \
"\t%s --output <directory>\n" % SCRIPT_NAME + \
"\n" + \
"Specify a new base directory, overriding the previous one\n" + \
"(this will not delete the previous base directory)\n" + \
"\t%s -F --output <directory>\n" % SCRIPT_NAME + \
"\n" + \
"Reset the configuration file, this will reset all configuration data and paths,\n" + \
"users can specify a new path to the base directory here\n" + \
"\t%s -R --output <directory>\n" % SCRIPT_NAME + \
"\n"

def setup_parser(parser):
    parser.description = DESCRIPTION
    parser.epilog = EPILOG
    parser.add_argument("-o",
                        "--output",
                        type = str,
                        nargs = 1,
                        help = "Specify a base directory")
    parser.add_argument( "-F",
                        "--force",
                        action="store_true",
                        help = "Override the current base directory and specify a new one")
    parser.add_argument("-R",
                        "--reset",
                        action="store_true",
                        help = "Reset both the configuration file and user base dir")

    return parser

def init(args, status):
    s = status
    base_path = site_manager.DEFAULT_USER_BASE
    sm = site_manager.SiteManager(status)
    paths_dict = sm.get_paths_dict()

    #Check if the base that is in the paths dictionary exists or the user is forcing a new dictionary
    if (not os.path.exists(paths_dict["nysa_user_base"])) or args.force or args.reset:
        if s: s.Important("User base directory doesn't exists or a force or reset is detected")
        base_path = paths_dict["nysa_user_base"]
        base_path = site_manager.DEFAULT_USER_BASE
        #This is uniitializes nysa base
        if args.output is not None:
            base_path = os.path.expanduser(args.output[0])

        paths_dict["nysa_user_base"] = base_path

    elif args.output is not None:
        if args.output[0] != paths_dict["nysa_user_base"]:
            if s: s.Error("Specifying an output directory when one already exists!, use -F or -R to force a new directory")
            sys.exit(-1)
     
    paths_dict["nysa_user_base"] = base_path
    if s: s.Debug("Paths dict:\n%s" % json.dumps(paths_dict, sort_keys = True, indent = 2, separators=(",", ": ")))

    #Check to see if the final directory has been generated
    #Verilog Path
    vpath = os.path.join(base_path, "verilog")
    #Examples Path
    epath = os.path.join(base_path, "examples")
    #Dev Path
    dev_path = os.path.join(base_path, "dev")
    #Apps Path
    app_path = os.path.join(base_path, "apps")

    if not os.path.exists(base_path):
        if s: s.Important("Generating nysa base directory")
        os.makedirs(base_path)
    if not os.path.exists(vpath):
        #Make the verilog directory
        if s: s.Important("Generating verilog directory")
        vpath = os.path.join(base_path, "verilog")
        os.makedirs(vpath)
    if not os.path.exists(epath):
        #Make the examples directory
        if s: s.Important("Generating examples directory")
        epath = os.path.join(base_path, "examples")
        os.makedirs(epath)
    if not os.path.exists(dev_path):
        #make the dev directory
        if s: s.Important("Generating dev directory")
        dev_path = os.path.join(base_path, "dev")
        os.makedirs(dev_path)
    if not os.path.exists(app_path):
        #Make the application directory
        if s: s.Important("Generating apps directory")
        app_path = os.path.join(base_path, "apps")
        os.makedirs(app_path)


