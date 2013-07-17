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
import shutil

MAP_DEFAULT_FLAG_FILE = "map_default_flags.json"
MAP_DIR = "map"
SMARTGUIDE_NAME = "smartguide_map.ncd"

def smartguide_available(config):
    """
    Check to see if there is an .ncd file from a previous build,
    if so it can be used to speed up the build of the design
   
    Args:
        config (dictionary): configuration dictionary

    Return:
        (boolean):
            True: Available
            False: Not Available

    Raises:
        Nothing
    """
    #Check to see if the output file exists
    map_file = get_map_filename(config, absolute = True)
    
    if os.path.exists(map_file):
        sg_file = get_smartguide_filename(config, absolute = True)
        shutil.copy2(map_file, sg_file)
        #There is a previous version
        return True

    return False

def get_smartguide_filename(config, absolute = False):
    """
    Get the smartguide filename for map

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): smartguide filename

    Raises:
        Nothing
    """
    map_dir = get_map_dir(config, absolute)
    map_file = os.path.join(map_dir, SMARTGUIDE_NAME)
    #print "map filename: %s" % map_file
    return map_file


def get_map_flags(config):
    """
    Given a configuration dictionary return flags for the MAP build
    if user flags are not specified take the default flags from

    site_scons/map_default_flags.json

    Args:
        config (dictionary): configuration dictionary

    Return:
        (dictionary): flag dictionary

    Raises:
        Nothing
    """
    flags = {}
    user_flags = {}
    if "map" in config.keys():
        if "flags" in config["map"].keys():
            user_flags = config["map"]["flags"]
    fn = os.path.join(os.path.dirname(__file__), MAP_DEFAULT_FLAG_FILE)

    default_flags = json.load(open(fn, "r"))
    default_flags["-p"]["value"] = config["device"]
    default_flags["-o"]["value"] = get_map_filename(config, absolute = True)
    if smartguide_available(config):
        default_flags["-smartguide"]["value"] = get_smartguide_filename(config, True)
    else:
        default_flags["-timing"]["value"] = "_true"

    for key in default_flags:
        flags[key] = default_flags[key]
        if key in user_flags.keys():
            flags[key]["value"] = user_flags[key]
    return flags


def create_map_dir(config):
    """
    Create an map directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): map output directory (relative)

    Raises:
        Nothing
    """
    #Create a output directory if it does not exist
    build_dir = utils.create_build_directory(config)
    #Now I have an output directory to put stuff in
    #Create an XST directory to put stuff related to XST
    map_dir = os.path.join(build_dir, MAP_DIR)
    if not os.path.exists(map_dir):
        os.makedirs(map_dir)
    return map_dir

def get_map_dir(config, absolute = False):
    """Returns the map output directory location

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
    map_dir = os.path.join(build_dir, MAP_DIR)
    return map_dir

def get_map_filename(config, absolute=False):
    """get the output filename"""
    map_dir = get_map_dir(config, absolute)
    top_module = config["top_module"]
    map_file = os.path.join(map_dir, "%s.ncd" % top_module)
    #print "map filename: %s" % map_file
    return map_file

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
    flags = get_map_flags(config)
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

