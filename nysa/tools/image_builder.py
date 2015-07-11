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
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import sys
import os
import shutil
import urllib2


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

from nysa.ibuilder.lib import ibuilder

EXAMPLE_DIR = os.path.join("home", "user", "Projects", "nysa", "ibuilder", "example_project", "dionyus_default.json")

ALIAS = "ib"
NAME = "image-builder"
SCRIPT_NAME = "nysa %s" % NAME

__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "create a vendor specific project to generate an image for a platform"

EPILOG = "\n" \
         "Examples:\n" + \
         "\n" + \
         "Generate an ibuilder project directory:\n" + \
         "\t%s %s\n" % (SCRIPT_NAME, EXAMPLE_DIR) + \
         "\n" + \
         "Generate an ibuilder project directory then compress using tar/gzip format:\n" + \
         "\t%s -c %s\n" % (SCRIPT_NAME, EXAMPLE_DIR) + \
         "\n" + \
         "Generate an ibuilder project directory then compress using zip format:\n" + \
         "\t%s -z %s\n" % (SCRIPT_NAME, EXAMPLE_DIR) + \
         "\n"


def create_directory_structure(root=None, debug=False):
    if root is None:
        raise IOError("Root is None!")

    mfiles = []
    for root, dirs, files in os.walk(root):
        for d in dirs:
            create_directory_structure(d, debug=debug)

        for f in files:
            fadd = os.path.join(root, f)
            if debug: print("+ %s" % fadd)
            mfiles.append(fadd)

    return mfiles


def remove_output_project(root=None, debug=False):
    if root is None:
        raise IOError("Root is None!")

    for root, dirs, files in os.walk(root):
        for d in dirs:
            ex_d = os.path.join(root, d)
            remove_output_project(ex_d, debug=debug)
            if os.path.exists(ex_d):
                os.removedirs(ex_d)

        for f in files:
            if debug: print("Removing %s" % os.path.join(root, f))
            os.remove(os.path.join(root, f))

    try:
        os.removedirs(root)
    except:
        pass


def setup_parser(parser):
    # Add an argument to the parser

    parser.description = DESCRIPTION
    parser.epilog = EPILOG
    parser.alias = ALIAS

    parser.add_argument("-o", "--output", type=str, nargs=1, default="",
                        help="Specify a location for the generated project")
    parser.add_argument("-c", "--compress", action='store_true', help="Compress output project in tar gzip format")
    parser.add_argument("-z", "--zip", action='store_true', help="Compress output project in zip format")
    parser.add_argument("config", type=str, nargs=1, default="all", help="Configuration file to load")
    return parser


def image_builder(args, status):
    output_dir = None
    s = status

    s.Debug("Generating Project: %s" % args.config[0])
    if len(args.output) > 0:
        output_dir = args.output[0]

    # ibuilder.generate_project(args.config[0], dbg = debug)
    # ibuilder.generate_project(args.config[0], output_directory = output_dir, status = s)
    try:
        ibuilder.generate_project(args.config[0], output_directory=output_dir, status=s)
    except urllib2.URLError as ex:
        s.Fatal("URL Error: %s, Are you connected to the internet?" % str(ex))
        sys.exit(1)

    if output_dir is None:
        output_dir = ibuilder.get_output_dir(args.config[0])

    s.Info("Generating Project %s @ %s" % (args.config[0], output_dir))

    if args.compress:
        output_dir = ibuilder.get_output_dir(args.config[0], dbg=args.debug)
        name = os.path.split(output_dir)[1]
        out_loc = os.path.split(output_dir)[0]

        s.Debug("Current dir: %s" % os.getcwd())
        s.Debug("Output Location: %s" % out_loc)
        s.Debug("archive name: %s" % name)

        archive_loc = os.path.join(out_loc, name)

        s.Debug("Compress using gztar format")
        name = shutil.make_archive(base_name=archive_loc,
                                   format='gztar',
                                   root_dir=out_loc,
                                   base_dir=name)
        remove_output_project(output_dir, debug=args.debug)

    if args.zip:
        output_dir = ibuilder.get_output_dir(args.config[0], dbg=args.debug)
        name = os.path.split(output_dir)[1]
        out_loc = os.path.split(output_dir)[0]

        s.Debug("Current dir: %s" % os.getcwd())
        s.Debug("Output Location: %s" % out_loc)
        s.Debug("archive name: %s" % name)

        archive_loc = os.path.join(out_loc, name)

        s.Debug("Compress using zip format")
        name = shutil.make_archive(base_name=archive_loc,
                                   format='zip',
                                   root_dir=out_loc,
                                   base_dir=name)
        remove_output_project(output_dir, debug=args.debug)

