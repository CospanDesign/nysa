#! /usr/bin/python

#Distributed under the MIT licesnse.
#Copyright (c) 2012 Dave McCoy (dave.mccoy@cospandesign.com)

#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in m
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


__author__ = "dave.mccoy@cospandesign.com (Dave McCoy)"

import sys
import os
import argparse
import inspect
import unittest


sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, 'gui/plugins'))

gui_plugin_dir  = os.path.join(os.path.dirname(__file__), os.pardir, "gui/plugins")



DESCRIPTION = "\n" \
"Nysa Test Manager\n" \
"\n" \
"Test a subset or all of the modules within Nysa\n" \


EPILOG = "\n" \
"Examples: \n" \
"\n" \
"Test all modules\n"
"\ttest_nysa.py all"



def get_tests(base_dir):
  temp_files = []


  test_modules = []
  tl = unittest.TestLoader()
  temp_list = tl.discover(base_dir, pattern = "test*.py", top_level_dir="../")
  for t in temp_list:
    print "test: %s" % str(temp_list)
    if t.countTestCases() != 0:
      test_modules.extend(t)

  return test_modules


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=DESCRIPTION,
    epilog=EPILOG)
  #parser.add_argument("echo")
  parser.add_argument("-l", "--list", help="Displays a list of tests to run", action="store_true")
  parser.add_argument("-d", "--debug", help="Enable debugging of user tests", action="store_true")
  parser.add_argument("-v", "--verbose", help="Display more information in tests", action="store_true")
  parser.add_argument("test", nargs="?", type=str, help="Type the name of the test to run", default="go")
  parser.parse_args()
  args = parser.parse_args()

  if args.list:
    test_files = []
    print "The following tests are available"
    test_files.extend(get_tests(gui_plugin_dir))
    print "plugin tests: %s" % str(test_files)
    for t in test_files:
      print "%s is %s" % (str(t), str(type(t)))

  else:
    if args.test == "go":
      print "run all tests"
      test_files = []
      test_files.extend(get_tests(gui_plugin_dir))
      test_files.debug()
      print "run gui plugins test..."
      print "run host tests..."
      print "run local tests..."


    if args.test == "s":
      print "don't run all"

    if args.test == "plugins":
      print "gui plugin dir: %s: " % gui_plugin_dir
      print "Testing plugins"



