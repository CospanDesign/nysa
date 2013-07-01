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
import copy

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


def parse_signal_range(signal, debug = False):
    """
    Returns a signal and a range in a tuple

    (name, max, min)
    """

    rng = ""
    name = ""
    maximum = ""
    minimum = ""
    signal = signal.strip()
    name = signal
    if debug: print "Start signal: %s" % signal

    if "[" in signal:
        rng = signal.partition("[")[2]
        if ":" not in rng:
            minimum = int(rng.strip("]"))
            maximum = int(minimum)
            if debug: print "Signal signal range: %s" % minimum
        else:
            minimum = rng.partition(":")[2]
            minimum = minimum.strip("]")
            minimum = minimum.strip()
            minimum = int(minimum)
            maximum = rng.partition(":")[0]
            maximum = maximum.strip()
            maximum = int(maximum)
        name = signal.partition("[")[0]

    name = name.strip()
    if debug: print "Final Signals: %s, %d, %d" % (name, maximum, minimum)
    return (name, maximum, minimum)

def has_range(signal):
    rng = ""
    name = ""
    maximum = ""
    minimum = ""

    if "[" in signal:
        rng = signal.partition("[")[2]
        if ":" not in rng:
            minimum = rng.strip("]")
            maximum = minimum
        else:

            rng = signal.partition("[")[2]
            minimum = rng.partition(":")[2]
            minimum = minimum.strip("]")
            minimum = minimum.strip()
            minimum = int(minimum)
            maximum = rng.partition(":")[0]
            maximum = maximum.strip()
            maximum = int(maximum)
            name = signal.partition("[")[0]

        #XXX: Probably could be imporved, what about the case with a signal like: signal[0]
        return True

    return False


def expand_user_constraints(user_dict, debug = False):
    #if debug: print "User Dictionary: %s" % str(user_dict)
    ex_dict = {}
    signal = ""
    maximum = -1
    minimum = -1
    signal_range = {}
    is_range = False
    port_is_range = False
    port_name = ""
    port_min = -1
    port_max = -1
    port_range = {}
    for key in user_dict:
        if debug: print "Working on %s" % key
        if has_range(key):
            signal_range = {}
            port_range = {}
            signal, maximum, minimum = parse_signal_range(key)
            is_range = True
            for i in range (len(range(minimum, maximum + 1))):
                signal_range[i] = minimum + i

            if has_range(user_dict[key]["pin"]):
                #The pin is a range too
                port_name, port_max, port_min = parse_signal_range(user_dict[key]["pin"])
                for i in range (len(range(port_min, port_max + 1))):
                    port_range[i] = port_min + i
                port_is_range = True
            else:
                #There is only one pin
                if debug: print "Found only one pin: %s" % user_dict[key]["pin"]
                port_is_range = False
                port_name = user_dict[key]["pin"]
                if signal not in ex_dict:
                    ex_dict[signal] = {}
                    ex_dict[signal]["range"] = False
                else:
                    ex_dict[signal]["range"] = True
                ex_dict[signal][minimum] = {}
                ex_dict[signal][minimum]["direction"] = user_dict[key]["direction"]
                ex_dict[signal][minimum]["pin"] = user_dict[key]["pin"]
                continue


        else:
            signal = key
            is_range = False
            port_name = user_dict[key]["pin"]

        if signal not in ex_dict:
            ex_dict[signal] = {}

        if not is_range:
            ex_dict[signal]["direction"] = user_dict[key]["direction"]
            ex_dict[signal]["pin"] = user_dict[key]["pin"]
            ex_dict[signal]["range"] = False
        else:
            ex_dict[signal]["range"] = True
            for i in range(len(range(minimum, maximum + 1))):
                val = signal_range[i]
                #print "signal: %s" % signal
                #print "Port range: %s" % str(port_range)
                port_val = port_range[i]
                if debug: print "Value: %d" % val
                if debug: print "Port Value: %d" % port_val
                ex_dict[signal][val] = {}
                ex_dict[signal][val]["direction"] = user_dict[key]["direction"]
                if port_is_range:
                    ex_dict[signal][val]["pin"] = "%s[%d]" % (port_name, port_val)
                else:
                    ex_dict[signal][val]["pin"] = user_dict[key]["pin"]

    #if debug: print "ex_dict: %s" % str(ex_dict)
    return ex_dict

def consolodate_constraints(cdict, debug = False):
    cdict = copy.deepcopy(cdict)
    user_dict = {}
    if debug: print "user_dict: %s" %  str(user_dict)
    for key in cdict.keys():
        if debug: print "Working on: %s" % key
        if not cdict[key]["range"]:
            user_dict[key] = {}
            user_dict[key]["direction"] = cdict[key]["direction"]
            user_dict[key]["pin"] = cdict[key]["pin"]
        else:

            def done(out_dict, signal, start_index, end_index, direction, pin_name, pin_start_index, pin_end_index):
                #only for the case of ranges (even a range of 1)
                sig = ""
                if start_index == end_index:
                    sig = "%s[%d]" % (signal, start_index)
                else:
                    sig = "%s[%d:%d]" % (signal, end_index, start_index)
                out_dict[sig] = {}
                out_dict[sig]["direction"] = direction
                pin = ""
                if pin_start_index == -1:
                    pin = pin_name
                elif pin_start_index == end_index:
                    pin = "%s[%d]" % (pin_name, pin_start_index)
                else:
                    pin = "%s[%d:%d]" % (pin_name, pin_end_index, pin_start_index)
                out_dict[sig]["pin"] = pin

            prev_val = None
            prev_pin_val = None
            start_index = -1
            start_pin_index = -1
            start_dir = None
            start_pin_name = None
            start_pin_index = None
            td = cdict[key]
            signal_indexes = td.keys()
            signal_indexes.remove("range")
            signal_indexes.sort()

            if debug: print "Working through a range"
            if debug: print "Start_index: %s" % signal_indexes[0]

            while (signal_indexes):
                #Still some signals left

                if debug: print "signals: %s" % str(signal_indexes)

                #Get the first (lowest value)
                start_index = signal_indexes.pop(0)
                start_dir = td[start_index]["direction"]
                pin = td[start_index]["pin"]

                if not has_range(pin):
                    #There is only one signal
                    if debug: print "pin (%s) does not have range" % pin
                    done(user_dict, key, start_index, start_index, start_dir, pin, -1, -1)
                    continue

                start_pin_name, start_pin_index, _ = parse_signal_range(pin, debug)

                if debug: print "Start Pin Name: %s" % start_pin_name
                if debug: print "Start pin index: %s" % start_pin_index
                if debug: print "Start_direction: %s" % start_dir

                #set up to analyze the series
                current_index = start_index
                current_pin_index = start_pin_index

                next_index = current_index + 1
                signal_search = True
                while (next_index in signal_indexes) and signal_search:
                    #there is a consecutive signal in here
                    if debug: print "Looking for the next signal index: %d" % next_index
                    if (td[next_index]["direction"] != start_dir):
                        if debug: print "current dir is not the same as start dir %s != %s" % (start_dir, td[next_index]["direction"])
                        done(user_dict,
                             key,
                             start_index,
                             current_index,
                             start_dir,
                             start_pin_name,
                             start_pin_index,
                             current_pin_index)
                        signal_search = False
                        break

                    #Directions match up
                    #get the current pin
                    pin = td[next_index]["pin"]
                    if not has_range(pin):
                        if debug: print "current pin: %s has no range" % (pin)
                        done(user_dict,
                             key,
                             start_index,
                             current_index,
                             start_dir,
                             start_pin_name,
                             start_pin_index,
                             current_pin_index)
                        signal_search = False
                        break

                    next_pin_name, next_pin_index, _ = parse_signal_range(pin)

                    if next_pin_name != start_pin_name or next_pin_index != (current_pin_index + 1):
                        if next_pin_name != start_pin_name:
                            if debug: print "start pin name not equal to current pin name: %s != %s" % (start_pin_name, next_pin_name)
                            pass
                        else:
                            if debug: print "Next pin index not equal to current pin index: %d + 1 != %d" % (current_pin_index, next_pin_index)
                            pass
                        done(user_dict,
                             key,
                             start_index,
                             current_index,
                             start_dir,
                             start_pin_name,
                             start_pin_index,
                             current_pin_index)
                        signal_search = False
                        break

                    #passed the gauntlet
                    if debug: print "Passed the gauntlet"
                    current_index = next_index
                    current_pin_index = next_pin_index
                    signal_indexes.remove(current_index)
                    if not signal_indexes:
                        if debug: print "No more signals"
                        done(user_dict,
                             key,
                             start_index,
                             current_index,
                             start_dir,
                             start_pin_name,
                             start_pin_index,
                             current_pin_index)
                        signal_search = False
                        break

                    next_index = current_index + 1
                    next_pin_index = current_pin_index + 1



    if debug: print "user_dict: %s" % str(user_dict)

    return user_dict



