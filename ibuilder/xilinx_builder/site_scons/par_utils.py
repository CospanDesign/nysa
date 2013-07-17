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
import shutil

import utils

PAR_DEFAULT_FLAG_FILE = "par_default_flags.json"
PAR_DIR = "par"
SMARTGUIDE_NAME = "smartguide_par.ncd"


def smartguide_available(config):
    """
    Check to see if there is an _par.ncd file from a previous build,
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
    par_file = get_par_filename(config, absolute = True)
    if os.path.exists(par_file):
        sg_file = get_smartguide_filename(config, absolute = True)
        shutil.copy2(par_file, sg_file)
        return True
    return False

def get_smartguide_filename(config, absolute = False):
    """
    Get the smartguide filename for par

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): smartguide filename

    Raises:
        Nothing
    """
    par_dir = get_par_dir(config, absolute = True)
    return os.path.join(par_dir, SMARTGUIDE_NAME)

def get_par_flags(config):
    """
    Given a configuration dictionary return flags for the PAR build
    if user flags are not specified take the default flags from

    site_scons/par_default_flags.json

    Args:
        config (dictionary): configuration dictionary

    Return:
        (dictionary): flag dictionary

    Raises:
        Nothing
    """
    flags = {}
    user_flags = {}
    if "par" in config.keys():
        if "flags" in config["par"].keys():
            user_flags = config["par"]["flags"]
    fn = os.path.join(os.path.dirname(__file__), PAR_DEFAULT_FLAG_FILE)

    default_flags = json.load(open(fn, "r"))

    #if we can do smart guide go for it
    #if smartguide_available(config):
    #    default_flags["-smartguide"]["value"] = get_smartguide_filename(config, True)

    for key in default_flags:
        flags[key] = default_flags[key]
        if key in user_flags.keys():
            flags[key]["value"] = user_flags[key]
    return flags

def create_par_dir(config):
    """
    Create an par directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): par output directory (relative)

    Raises:
        Nothing
    """
    #Create a output directory if it does not exist
    build_dir = utils.create_build_directory(config)
    #Now I have an output directory to put stuff in
    #Create an XST directory to put stuff related to XST
    par_dir = os.path.join(build_dir, PAR_DIR)
    if not os.path.exists(par_dir):
        os.makedirs(par_dir)
    return par_dir

def get_par_dir(config, absolute = False):
    """Returns the par output directory location

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
    par_dir = os.path.join(build_dir, PAR_DIR)
    return par_dir

def get_par_filename(config, absolute=False):
    """get the output filename"""
    par_dir = get_par_dir(config, absolute)
    top_module = config["top_module"]
    par_file = os.path.join(par_dir, "%s_par.ncd" % top_module)
    #print "par filename: %s" % par_file
    return par_file

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
    flags = get_par_flags(config)
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

