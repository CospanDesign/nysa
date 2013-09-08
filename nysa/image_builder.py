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
import zipfile
import shutil

base = os.path.join( os.path.dirname(__file__),
                     os.pardir)
nysa_base = os.path.abspath(base)

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from ibuilder.lib import ibuilder

example_dir = os.path.join(nysa_base, "ibuilder", "example_project", "dionysus_gpio_mem.json")


__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

DESCRIPTION = "\n" \
"Create Nysa Image Projects\n"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"Generate an ibuilder project directory:\n" + \
"\tibuilder.py %s\n" % example_dir + \
"\n" + \
"Generate an ibuilder project directory then compress using tar/gzip format:\n" + \
"\tibuilder.py -c %s\n" % example_dir + \
"\n" + \
"Generate an ibuilder project directory then compress using zip format:\n" + \
"\tibuilder.py -z %s\n" % example_dir + \
"\n"


def create_directory_structure(root = None, debug = False):
  if root is None:
    raise IOError ("Root is None!")

  mfiles = []
  for root, dirs, files in os.walk(root):
    for d in dirs:
      create_directory_structure(d, debug = debug)

    for f in files:
      fadd = os.path.join(root, f)
      if debug: print "+ %s" % fadd
      mfiles.append(fadd)
 
  return mfiles

def remove_output_project(root = None, debug = False):
  if root is None:
    raise IOError ("Root is None!")

  for root, dirs, files in os.walk(root):
    for d in dirs:
      ex_d = os.path.join(root, d)
      remove_output_project(ex_d, debug = debug)
      if os.path.exists(ex_d):
        os.removedirs(ex_d)


    for f in files:
      if debug: print "Removing %s" % os.path.join(root, f)
      os.remove(os.path.join(root, f))

  try:
    os.removedirs(root)
  except:
    pass


if __name__ == "__main__":

  parser = argparse.ArgumentParser(
  formatter_class=argparse.RawDescriptionHelpFormatter,
    description=DESCRIPTION,
    epilog=EPILOG
  )

  debug = False

  #Add an argument to the parser
  parser.add_argument("-d", "--debug", action='store_true', help="Output test debug information")
  parser.add_argument("-c", "--compress", action='store_true', help="Compress output project in tar gzip format")
  parser.add_argument("-z", "--zip", action='store_true', help="Compress outptu project in zip format")
  parser.add_argument("config", type = str, nargs=1,  default="all", help="Configuration file to load")
  parser.parse_args()
  args = parser.parse_args()

  if args.debug:
    print "Debug Enable"
    print "Nysa Base: %s" % nysa_base
    debug = True

  if debug: print "Generating project %s" % args.config[0]
  #ibuilder.generate_project(args.config[0], dbg = debug)
  ibuilder.generate_project(args.config[0], dbg = False)
  if debug: print "Generated project %s" % args.config[0]

  if args.compress:
    output_dir = ibuilder.get_output_dir(args.config[0], dbg=debug)
    name = os.path.split(output_dir)[1]
    out_loc = os.path.split(output_dir)[0]

    if debug: print "Current dir: %s" % os.getcwd()
    if debug: print "Output Location: %s" % out_loc
    if debug: print "archive name: %s" % name

    archive_loc = os.path.join(out_loc, name)


    if debug: print "Compress using gztar format"
    name = shutil.make_archive( base_name = archive_loc,
                                format = 'gztar',
                                root_dir = out_loc,
                                base_dir = name,
                                )
    remove_output_project(output_dir, debug=debug)

  if args.zip:
    output_dir = ibuilder.get_output_dir(args.config[0], dbg=debug)
    name = os.path.split(output_dir)[1]
    out_loc = os.path.split(output_dir)[0]

    if debug: print "Current dir: %s" % os.getcwd()
    if debug: print "Output Location: %s" % out_loc
    if debug: print "archive name: %s" % name

    archive_loc = os.path.join(out_loc, name)


    if debug: print "Compress using zip format"
    name = shutil.make_archive( base_name = archive_loc,
                                format = 'zip',
                                root_dir = out_loc,
                                base_dir = name,
                                )
    remove_output_project(output_dir, debug=debug)

