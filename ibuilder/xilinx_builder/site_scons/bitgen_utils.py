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

BITGEN_DEFAULT_FLAG_FILE = "bitgen_default_flags.json"
BITGEN_CONFIG_FILE = "bitgen_configuration.json"
BITGEN_DIR = "bitgen"
BITGEN_SCRIPT_FN = "bitgen_script.ut"

def get_flags(config):
    """
    Given a configuration dictionary return flags for the BITGEN build
    if user flags are not specified take the default flags from

    site_scons/bitgen_default_flags.json

    Args:
        config (dictionary): configuration dictionary

    Return:
        (dictionary): flag dictionary

    Raises:
        Nothing
    """
    flags = {}
    user_flags = {}
    bg_config = {}
    if "bitgen" in config.keys():
        if "flags" in config["bitgen"].keys():
            user_flags = config["bitgen"]["flags"]
        if "config" in config["bitgen"].keys():
            bg_config = config["bitgen"]["flags"]

    fn = os.path.join(os.path.dirname(__file__), BITGEN_DEFAULT_FLAG_FILE)
    cfg_fn = os.path.join(os.path.dirname(__file__), BITGEN_CONFIG_FILE)

    #Get a dictionary to the default flags
    default_flags = json.load(open(fn, "r"))
    for key in default_flags:
        if key == "-g":
            #Take care of all the configuration settings below
            continue

        if key in user_flags.keys():
            default_flags[key]["value"] = user_flags[key]["value"]

        #If the value is empty don't put it in
        if len(default_flags[key]["value"]) == 0:
            continue

        flags[key] = default_flags[key]["value"]



    #Get a dictionary of the configuration data
    default_config = json.load(open(cfg_fn, "r"))
    flags["configuration"] = []
    cfg = flags["configuration"]
    for key in default_config:
        if key in config["bitgen"]["config"].keys():
            #User has overriden default values
            default_config[key]["value"] = config["bitgen"]["config"][key]
        if len(default_config[key]["value"]) == 0:
            continue

        cfg.append("-g %s:%s" % (key, default_config[key]["value"]))
    return flags

def create_bitgen_dir(config):
    """
    Create an bitgen directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): bitgen output directory (relative)

    Raises:
        Nothing
    """
    #Create a output directory if it does not exist
    build_dir = utils.create_build_directory(config)
    #Now I have an output directory to put stuff in
    #Create an XST directory to put stuff related to XST
    bitgen_dir = os.path.join(build_dir, BITGEN_DIR)
    if not os.path.exists(bitgen_dir):
        os.makedirs(bitgen_dir)
    return bitgen_dir

def get_bitgen_dir(config, absolute = False):
    """Returns the bitgen output directory location

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
    bitgen_dir = os.path.join(build_dir, BITGEN_DIR)
    return bitgen_dir

def get_bitgen_filename(config, absolute=False):
    """get the output filename"""
    bitgen_dir = get_bitgen_dir(config, absolute)
    top_module = config["top_module"]
    bitgen_file = os.path.join(bitgen_dir, "%s.bit" % top_module)
    #print "bitgen filename: %s" % bitgen_file
    return bitgen_file

def get_bitgen_script_filename(config, absolute = False):
    """
    Returns the Bitgen Script filename

    Args:
        config (dictionary): configuration dictionary

    Returns:
        (string): configuration dictionary filename
    """
    bitgen_dir = get_bitgen_dir(config, absolute)
    bitgen_script_fn = os.path.join(bitgen_dir, BITGEN_SCRIPT_FN)
    return bitgen_script_fn


def create_script(config):
    """
    Create a script file to feed into bitgen.

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string) script file name

    Raises:
        Nothing
    """
    create_bitgen_dir(config)
    bgs_fn = get_bitgen_script_filename(config, True)
    #Get all the flags in a digestible form
    flags = get_flags(config)

    bgs = open(bgs_fn, "w")
    for flag in flags:
        if flag == "configuration":
            #Handle configuration below
            continue
        if flags[flag] == "_true":
            bgs.write("%s%s" % (flag, os.linesep))
            #Special Case where flag is by itself
            continue
        bgs.write("%s %s%s" % (flag, flags[flag], os.linesep))

    bgs.write("%s" % os.linesep)

    #Add all the configuration sub options to the mix
    for c in flags["configuration"]:
        bgs.write("%s%s" % (c, os.linesep))

    bgs.close()
    return bgs_fn

