#! /usr/bin/python

#Distributed under the MIT licesnse.
#Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

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

"""Unit test controller

Description: A command line unit test controller, put this in the directory
of python unit test, the names of the files need to start with 'test_' and
end with '.py' it will do the rest

"""

"""
Log:

5/27/2013: Initial commit, many of this code was taken from the Olympus 
  'run_test.py' script
"""


import sys
import os
import argparse
import unittest

DESCRIPTION = "\n" \
"Run unit/integration tests of all colors and flavors\n"

EPILOG = "\n" \
"Examples:\n" + \
"\n" + \
"Run all tests:\n" + \
"\ttester.py\n" + \
"\n" + \
"List the available tests:\n" + \
"\ttester.py -l\n" + \
"\n" + \
"Run a specific test:\n" + \
"\ttester.py <test name>\n" + \
"Run a specific/all tests with lots of debug info\n" + \
"\ttester.py -d [test name]"


debug = False

base = os.path.join( os.path.dirname(__file__),
                     os.pardir)
nysa_base = os.path.abspath(base)



def get_tests_list():
  tests = []
  base = os.path.join( os.path.dirname(__file__),
                       os.pardir)
  nysa_base = os.path.abspath(base)

  for root, dir, testfiles in os.walk(nysa_base):
    for testfile in testfiles:
      if testfile.startswith("test_") and testfile.endswith("py"):
        f = testfile.partition("test_")[2]
        tests.append(f.partition(".")[0])


  return tests

def execute_test(arg):
  '''Run one/many/all tests'''
  if isinstance(arg, basestring):
    if arg == "all":
      if debug: print "Test all"
      tl = unittest.TestLoader()
      pt = tl.discover(os.path.dirname(__file__), pattern = "test*.py")
      print "Number of test cases: " + str(pt.countTestCases())
      pt.debug()
    else:
      if debug: print "Test: %s" % arg
      test = "test_%s.py" % arg
      tl = unittest.TestLoader()
      pt = tl.discover(os.path.dirname(__file__), pattern = test)
      if pt.countTestCases() != 0:
        if debug: print "Found test"
        pt.debug()

  elif isinstance(arg, list):
    testfiles = []
    if debug: print "Test a list of test: %s" % str(arg)



if __name__ == "__main__":
  parser = argparse.ArgumentParser(
  formatter_class=argparse.RawDescriptionHelpFormatter,
    description=DESCRIPTION,
    epilog=EPILOG
  )

  #Add an argument to the parser
  parser.add_argument("-d", "--debug", action='store_true', help="Output test debug information")
  parser.add_argument("-l", "--list", action='store_true', help="List all available test suits")
  parser.add_argument("test", type = str, nargs='?',  default="all", help="Run a test (Leave blank for all tests)")
  parser.parse_args()
  args = parser.parse_args()

  if args.debug:
    print "Debug Enable"
    print "Nysa Base: %s" % nysa_base
    debug = True

  if args.list:
    if debug: print "List all tests"

    tests = get_tests_list()
    print "Tests:"
    for test in tests:
      print "\t%s" % test

  if not args.list:
    if debug: print "Test: %s" % args.test
    execute_test(args.test)

