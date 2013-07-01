# Distributed under the MIT licesnse.
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
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Utilities used in detecting and generating wishbone cores"""

"""
Log:
06/27/2013
    -Initial Commit
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import string

from ibuilder_error import ConstraintError

def get_net_names(constraint_filename, debug = False):
    """Gets a list of net in a given constraint file

    Args:
        constrint_filename: name of a constraint file with an absolute path

    Returns:
        A list of constraint for the module
        NOTE: This file fails quietly and shouldn't this needs to be fixed!

    Raises:
        IBuilder Error
    """

    filename = ""
    buf = ""
    nets = []

    #open up the ucf file
    try:
        file_in = open(constraint_filename)
        buf = file_in.read()
        file_in.close()
    except:
        raise ConstraintError("Failed to open the filename %s" % constraint_filename)

    if debug:print "Opened up the UCF file"

    lines = buf.splitlines()
    #first search for the TIMESPEC keyword
    for line in lines:
        line = line.lower()
        #get rid of comments
        if ("#" in line):
            line = line.partition("#")[0]

        if "net" not in line:
            continue

        #split separate all space deliminated tokens
        line = line.partition("net")[2].strip()
        token = line.split()[0]
        token = token.strip("\"")

        token = token.replace('<', '[')
        token = token.replace('>', ']')
#        if debug:
#            print "possible net name: " + token

        if token not in nets:
            nets.append(token)

    return nets

def read_clock_rate(constraint_filename, debug = False):
    """Returns a string of the clock rate

    Searches through the specified constraint file to determine if there
    is a specified clock. If no clock is specified then return 50MHz = 50000000

    Args:
      constraint_filename: the name of the constraint file to search through

    Returns:
      A string representation of the clock rate
      NOTE: on error this fails quietly this should probably be different

    Raises:
      Nothing
    """
    clock_rate = ""

    #open up the ucf file
    try:
        file_in = open(constraint_filename)
        buf = file_in.read()
        file_in.close()
    except IOError as err:
        #XXX: This should probably allow the calling function to handle a failure
        #fail
        if debug: print "read clock rate error: %s" % str(err)
        raise ConstraintError("Failed to open file: %s" % constraint_filename)

    if debug: print "Opened up the UCF file"

    lines = buf.splitlines()
    #first search for the TIMESPEC keyword
    for line in lines:
        line = line.lower()
        #get rid of comments
        if ("#" in line):
            line = line.partition("#")[0]

        #is this the timespec for the "clk" clock?
        if ("timespec" in line) and ("ts_clk" in line):
            if debug: print "found timespec"
            #this is the "clk" clock, now read the clock value
            if debug: print "found TIMESPEC"
            line = line.partition("period")[2].strip()
            if debug: print "line: " + line
            line = line.partition("clk")[2].strip()
            line = line.strip("\"");
            line = line.strip();
            line = line.strip(";")
            if debug: print "line: " + line
            #now there is a time value and a multiplier
            clock_lines = line.split(" ")
            if debug:
              for line in clock_lines:
                print "line: " + line

            if (clock_lines[1] == "mhz"):
                clock_rate = clock_lines[0] + "000000"
            if (clock_lines[1] == "khz"):
                clock_rate = clock_lines[0] + "000"


    #if that didn't work search for the PERIOD keyword, this is an older version
    if (len(clock_rate) == 0):
        if debug: print "didn't find TIMESPEC, looking for period"
        #we need to check period
        for line in lines:
            #get rid of comments
            line = line.lower()
            if ("#" in line):
                line = line.partition("#")[0]
            if ("period" in line) and  ("clk" in line):
                if debug: print "found clock period"
                line = line.partition("period")[2]
                line = line.partition("=")[2].strip()
                if " " in line:
                    line = line.partition(" ")[0].strip()
                if debug: print "line: " + line
                clock_rate = str(int(1/(string.atoi(line) * 1e-9)))
                break;

    if debug: print "Clock Rate: " + clock_rate
    return clock_rate


