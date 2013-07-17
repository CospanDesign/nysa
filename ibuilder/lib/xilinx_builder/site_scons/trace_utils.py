#Distributed under the MIT licesnse.
#Copyright (c) 2013 Cospan Design (dave.mccoy@cospandesign.com)

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

import os
import json

import utils
import ngd_utils

TRACE_DEFAULT_FLAG_FILE = "trace_default_flags.json"
TRACE_DIR = "trace"

def get_trace_flags(config):
    """
    Given a configuration dictionary return flags for the TRACE build
    if user flags are not specified take the default flags from

    site_scons/trace_default_flags.json

    Args:
        config (dictionary): configuration dictionary

    Return:
        (dictionary): flag dictionary

    Raises:
        Nothing
    """
    flags = {}
    user_flags = {}
    if "trace" in config.keys():
        if "flags" in config["trace"].keys():
            user_flags = config["trace"]["flags"]
    fn = os.path.join(os.path.dirname(__file__), TRACE_DEFAULT_FLAG_FILE)

    default_flags = json.load(open(fn, "r"))

    #Setup some default values
    default_flags["-ucf"]["value"] = ngd_utils.get_ucf_filename(config)
    default_flags["-xml"]["value"] = get_trace_xml_filename(config)
    default_flags["-o"]["value"] = get_trace_filename(config)

    for key in default_flags:
        flags[key] = default_flags[key]
        if key in user_flags.keys():
            flags[key]["value"] = user_flags[key]
    return flags

def create_trace_dir(config):
    """
    Create a trace directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): trace output directory (relative)

    Raises:
        Nothing
    """
    #Create a output directory if it does not exist
    build_dir = utils.create_build_directory(config)
    #Now I have an output directory to put stuff in
    #Create an XST directory to put stuff related to XST
    trace_dir = os.path.join(build_dir, TRACE_DIR)
    if not os.path.exists(trace_dir):
        os.makedirs(trace_dir)
    return trace_dir

def get_trace_dir(config, absolute = False):
    """Returns the trace output directory location

    Args:
        config (dictionary): configuration dictionary
        absolute (boolean):
            False (default): Relative to project base
            True: Absolute

    Returns:
        (string): string representation of the path to the output

    Raises:
        Nothing
    """
    build_dir = utils.get_build_directory(config, absolute)
    trace_dir = os.path.join(build_dir, TRACE_DIR)
    return trace_dir

def get_trace_filename(config, absolute=False):
    """get the output filename"""
    trace_dir = get_trace_dir(config, absolute)
    top_module = config["top_module"]
    trace_file = os.path.join(trace_dir, "%s_trace.twr" % top_module)
    #print "trace filename: %s" % trace_file
    return trace_file

def get_trace_xml_filename(config, absolute=False):
    """Get the trace XML filename to put XML data into"""
    trace_dir = get_trace_dir(config, absolute)
    xml_filename = "%s.twx" % config["top_module"]
    xml_filename = os.path.join(trace_dir, xml_filename)
    return xml_filename

def get_build_flags_string(config):
    """Returns the flags for the build

    Args:
        config (dictionary): configuration dictionary

   Returns:
        (string): string of flags to be used on the command

    Raises:
        Nothing
    """
    flag_string = " "
    flags = get_trace_flags(config)
    for flag in flags:
        if len(flags[flag]["value"]) == 0:
            continue

        if flags[flag]["value"] == "_true":
            #Special case where we don't specify any variables
            flag_string += "%s " % flag
            continue
        
        #Normal flag
        flag_string += "%s %s " % (flag, flags[flag]["value"])

    return flag_string

