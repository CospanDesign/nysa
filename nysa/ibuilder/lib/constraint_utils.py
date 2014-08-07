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
import wishbone_utils as wu

def get_net_names_from_buffer(constraint_buffer, debug = False):
    nets = []
    lines = constraint_buffer.splitlines()
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
    buf = ""
    #open up the ucf file
    try:
        file_in = open(constraint_filename)
        buf = file_in.read()
        file_in.close()
    except:
        raise ConstraintError("Failed to open the filename %s" % constraint_filename)

    if debug:print "Opened up the UCF file"
    return get_net_names_from_buffer(buf)

def read_clock_rate_from_buffer(constraint_buffer, debug = False):
    clock_rate = ""
    lines = constraint_buffer.splitlines()
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

            if "ns" in line:
                #Working with a period not a frequency
                period = int(line.partition("ns")[0].strip())
                clock_rate = 1000000000 / period
                clock_rate = str(clock_rate)


            else:
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
    return read_clock_rate_from_buffer(buf, debug)

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
    loc_is_range = False
    loc_name = ""
    loc_min = -1
    loc_max = -1
    loc_range = {}
    for key in user_dict:
        if debug: print "Working on %s" % key
        if has_range(key):
            signal_range = {}
            loc_range = {}
            signal, maximum, minimum = parse_signal_range(key)
            is_range = True
            for i in range (len(range(minimum, maximum + 1))):
                signal_range[i] = minimum + i

            if has_range(user_dict[key]["loc"]):
                #The loc is a range too
                loc_name, loc_max, loc_min = parse_signal_range(user_dict[key]["loc"])
                for i in range (len(range(loc_min, loc_max + 1))):
                    loc_range[i] = loc_min + i
                loc_is_range = True
            else:
                #There is only one loc
                if debug: print "Found only one loc: %s" % user_dict[key]["loc"]
                loc_is_range = False
                loc_name = user_dict[key]["loc"]
                if signal not in ex_dict:
                    ex_dict[signal] = {}
                    ex_dict[signal]["range"] = False
                else:
                    ex_dict[signal]["range"] = True
                ex_dict[signal][minimum] = {}
                ex_dict[signal][minimum]["direction"] = user_dict[key]["direction"]
                ex_dict[signal][minimum]["loc"] = user_dict[key]["loc"]
                continue


        else:
            if "range" in user_dict[key].keys():
                return user_dict
            #print "Signal does not have range: %s" % key
            signal = key
            is_range = False
            loc_name = user_dict[key]["loc"]

        if signal not in ex_dict:
            ex_dict[signal] = {}

        if not is_range:
            ex_dict[signal]["direction"] = user_dict[key]["direction"]
            ex_dict[signal]["loc"] = user_dict[key]["loc"]
            ex_dict[signal]["range"] = False
        else:
            ex_dict[signal]["range"] = True
            for i in range(len(range(minimum, maximum + 1))):
                val = signal_range[i]
                #print "signal: %s" % signal
                #print "Port range: %s" % str(loc_range)
                loc_val = loc_range[i]
                if debug: print "Value: %d" % val
                if debug: print "Port Value: %d" % loc_val
                ex_dict[signal][val] = {}
                ex_dict[signal][val]["direction"] = user_dict[key]["direction"]
                if loc_is_range:
                    ex_dict[signal][val]["loc"] = "%s[%d]" % (loc_name, loc_val)
                else:
                    ex_dict[signal][val]["loc"] = user_dict[key]["loc"]

    #if debug: print "ex_dict: %s" % str(ex_dict)
    return ex_dict

'''
def consolodate_constraints(edict, debug = False):
    edict = copy.deepcopy(edict)
    user_dict = {}
    if debug: print "user_dict: %s" %  str(user_dict)
    for key in edict.keys():
        if debug: print "Working on: %s" % key
        if not edict[key]["range"]:
            user_dict[key] = {}
            user_dict[key]["direction"] = edict[key]["direction"]
            user_dict[key]["loc"] = edict[key]["loc"]
        else:

            def done(out_dict, signal, start_index, end_index, direction, loc_name, loc_start_index, loc_end_index):
                #only for the case of ranges (even a range of 1)
                sig = ""
                if start_index == end_index:
                    sig = "%s[%d]" % (signal, start_index)
                else:
                    sig = "%s[%d:%d]" % (signal, end_index, start_index)
                out_dict[sig] = {}
                out_dict[sig]["direction"] = direction
                loc = ""
                if loc_start_index == -1:
                    loc = loc_name
                elif loc_start_index == end_index:
                    loc = "%s[%d]" % (loc_name, loc_start_index)
                else:
                    loc = "%s[%d:%d]" % (loc_name, loc_end_index, loc_start_index)
                out_dict[sig]["loc"] = loc

            prev_val = None
            prev_loc_val = None
            start_index = -1
            start_loc_index = -1
            start_dir = None
            start_loc_name = None
            start_loc_index = None
            td = edict[key]
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
                loc = td[start_index]["loc"]

                if not has_range(loc):
                    #There is only one signal
                    if debug: print "loc (%s) does not have range" % loc
                    done(user_dict, key, start_index, start_index, start_dir, loc, -1, -1)
                    continue

                start_loc_name, start_loc_index, _ = parse_signal_range(loc, debug)

                if debug: print "Start Pin Name: %s" % start_loc_name
                if debug: print "Start loc index: %s" % start_loc_index
                if debug: print "Start_direction: %s" % start_dir

                #set up to analyze the series
                current_index = start_index
                current_loc_index = start_loc_index

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
                             start_loc_name,
                             start_loc_index,
                             current_loc_index)
                        signal_search = False
                        break

                    #Directions match up
                    #get the current loc
                    loc = td[next_index]["loc"]
                    if not has_range(loc):
                        if debug: print "current loc: %s has no range" % (loc)
                        done(user_dict,
                             key,
                             start_index,
                             current_index,
                             start_dir,
                             start_loc_name,
                             start_loc_index,
                             current_loc_index)
                        signal_search = False
                        break

                    next_loc_name, next_loc_index, _ = parse_signal_range(loc)

                    if next_loc_name != start_loc_name or next_loc_index != (current_loc_index + 1):
                        if next_loc_name != start_loc_name:
                            if debug: print "start loc name not equal to current loc name: %s != %s" % (start_loc_name, next_loc_name)
                            pass
                        else:
                            if debug: print "Next loc index not equal to current loc index: %d + 1 != %d" % (current_loc_index, next_loc_index)
                            pass
                        done(user_dict,
                             key,
                             start_index,
                             current_index,
                             start_dir,
                             start_loc_name,
                             start_loc_index,
                             current_loc_index)
                        signal_search = False
                        break

                    #passed the gauntlet
                    if debug: print "Passed the gauntlet"
                    current_index = next_index
                    current_loc_index = next_loc_index
                    signal_indexes.remove(current_index)
                    if not signal_indexes:
                        if debug: print "No more signals"
                        done(user_dict,
                             key,
                             start_index,
                             current_index,
                             start_dir,
                             start_loc_name,
                             start_loc_index,
                             current_loc_index)
                        signal_search = False
                        break

                    next_index = current_index + 1
                    next_loc_index = current_loc_index + 1



    if debug: print "user_dict: %s" % str(user_dict)

    return user_dict
'''

def expand_ports(c_ports):
    """expand_ports

    Description: Expand ports to a format that is easier to modify

    Args:
        c_ports: ports that are consolodated (read directly from module_tags)

    Return:
        Dictionary of ports in an easier readible format

        [port][[range = T/F][?index] [direction]

    Raises:
        Nothing
    """
    d = {}
    #Go through all the ports, if there is a range, create a new 
    #setting within the output dictionary
    temp_dict = {}
    if (("input" in c_ports.keys()) or 
        ("output" in c_ports.keys()) or 
        ("inout" in c_ports.keys())):
        #need to translate this to a useful version
        temp_dict = copy.deepcopy(c_ports)
        c_ports = {}

        if "input" in temp_dict.keys():
            for key in temp_dict["input"]:
                c_ports[key] = {}
                c_ports[key] = temp_dict["input"][key]
                c_ports[key]["direction"] = "input"
        if "output" in temp_dict.keys():
            for key in temp_dict["output"]:
                c_ports[key] = {}
                c_ports[key] = temp_dict["output"][key]
                c_ports[key]["direction"] = "output"
        if "inout" in temp_dict.keys():
            for key in temp_dict["inout"]:
                c_ports[key] = {}
                c_ports[key] = temp_dict["inout"][key]
                c_ports[key]["direction"] = "inout"

    #for direction in c_ports:
    #    dir_ports = c_ports[direction]

    for port in c_ports:
        if "range" in c_ports[port]:
            return c_ports
        d[port] = {}
        #print "port: %s" % port
        size = c_ports[port]["size"]
        direction = c_ports[port]["direction"]
        if size == 1:
            d[port]["direction"] = direction
            d[port]["range"] = False
        else:
            min_val = c_ports[port]["min_val"]
            d[port]["range"] = True
            for i in range(min_val, min_val + size):
                d[port][i] = {}
                d[port][i]["direction"] = direction
    return d

def get_only_signal_ports(ports):
    """get_only_signal_ports

    Description: Remove all the bus signal as well as clock and reset

    Args:
        ports: port dictionary (this is supposed to have run through the
                expand ports function first

    Returns:
        Dictionary of ports without bus, clk or rst

    Raises:
        Nothing
    """
    d = {}
    for port in ports:
        if port == "clk":
            continue
        if port == "rst":
            continue
        if wu.is_wishbone_bus_signal(port):
            continue
        d[port] = ports[port]

    return d

def consolodate_ports(e_ports):
    """consolodate_ports

    Description: Transforms the dictionary to a format that can be used by the
    image generation scripts

    Args:
        e_ports: expanded ports

    Returns:
        Dictionary of the format
            [direction][port_name][(size), (? min_val), (? max_val)]

    """
    c_ports = {}

    i_ports = {}
    o_ports = {}
    io_ports = {}

    for port in e_ports:
        if e_ports[port]["range"]:
            indexes = e_ports[port].keys()
            indexes.remove("range")
            size = len(indexes)
            indexes.sort()
            min_val = indexes[0]
            max_val = min_val + size - 1
            if e_ports[port][min_val]["direction"] == "input":
                i_ports[port] = {}
                i_ports[port]["size"] = size
                i_ports[port]["min_val"] = min_val
                i_ports[port]["max_val"] = max_val

            if e_ports[port][min_val]["direction"] == "output":
                o_ports[port] = {}
                o_ports[port]["size"] = size
                o_ports[port]["min_val"] = min_val
                o_ports[port]["max_val"] = max_val

            if e_ports[port][min_val]["direction"] == "inout":
                io_ports[port] = {}
                io_ports[port]["size"] = size
                io_ports[port]["min_val"] = min_val
                io_ports[port]["max_val"] = max_val



        else:
            size = 1

            if e_ports[port]["direction"] == "input":
                i_ports[port] = {}
                i_ports[port]["size"] = size

            if e_ports[port]["direction"] == "output":
                o_ports[port] = {}
                o_ports[port]["size"] = size

            if e_ports[port]["direction"] == "inout":
                io_ports[port] = {}
                io_ports[port]["size"] = size



    if len(i_ports.keys()) > 0:
        c_ports["input"] = i_ports
    if len(o_ports.keys()) > 0:
        c_ports["output"] = o_ports
    if len(io_ports.keys()) > 0:
        c_ports["inout"] = io_ports
        
    return c_ports


