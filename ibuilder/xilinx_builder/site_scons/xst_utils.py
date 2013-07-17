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
import coregen_utils

XST_DEFAULT_FLAG_FILE = "xst_default_flags.json"
PROJECT_FILENAME = "project.prj"
XST_SCRIPT_FILENAME = "xst_script.xst"
XST_TEMP_DIR = "projnav.tmp"
XST_DIR = "xst"
XST_OUTFILE = "xst_out"
XST_PROJECT_LSO = "project.lso"

def get_xst_flags(config):
    """
    Given a configuration dictionary return flags for the XST build
    if user flags are not specified take the default flags from

    site_scons/xst_default_flags.json

    Args:
        config (dictionary): configuration dictionary

    Return:
        Dictionary of flags used to create the XST script

    Raises:
        Nothing
    """
    #print "Apply slave tags"
    flags = {}
    user_flags = {}
    if "xst" in config.keys():
        if "flags" in config["xst"].keys():
            user_flags = config["xst"]["flags"]

    fn = os.path.join(os.path.dirname(__file__), XST_DEFAULT_FLAG_FILE)
    default_flags = json.load(open(fn, "r"))
    for key in default_flags:
        flags[key] = default_flags[key]
        if key in user_flags.keys():
            flags[key]["value"] = user_flags[key]

    return flags


def create_xst_dir(config):
    """
    Create an xst directiroy in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): xst output directory (relative)

    Raises:
        Nothing
    """
    #Create a output directory if it does not exist
    build_dir = utils.create_build_directory(config)
    #Now I have an output directory to put stuff in
    #Create an XST directory to put stuff related to XST
    xst_dir = os.path.join(build_dir, XST_DIR)
    if not os.path.exists(xst_dir):
        os.makedirs(xst_dir)
    return xst_dir

def get_xst_dir(config, absolute = False):
    """Returns the xst output directory location

    Args:
        config (dictionary): configuration dictionary
        absolute (boolean):
            False (default): Relative to project base
            True: Absolute

    Returns:
        (string): strin representation of the path to the output

    Raises:
        Nothing
    """
    build_dir = utils.get_build_directory(config, absolute)
    xst_dir = os.path.join(build_dir, XST_DIR)
    return xst_dir


def create_temp_dir(config):
    """
    Create an xst temporary directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        Nothing

    Raises:
        Nothing
    """
    xst_dir = os.path.join(config["build_dir"], XST_DIR)
    temp_dir = os.path.join(xst_dir, XST_TEMP_DIR)
    temp_abs_dir = os.path.join(utils.get_project_base(), xst_dir, XST_TEMP_DIR)
    if not os.path.exists(temp_abs_dir):
        os.makedirs(temp_abs_dir)
    return temp_dir

def create_xst_project_file(config):
    """
    Given a configuration file create the .prj which holds the verilog
    filenames to be built

    Args:
        config (dictionary): configuration dictionary

    Return:
        Nothing

    Raises:
        Nothing
    """
    #print "Creating xst project file"
    xst_dir = create_xst_dir(config)
    project_fn = os.path.join(xst_dir, PROJECT_FILENAME)
    
    fp = open(project_fn, "w")
    v = ""
    #XXX: There should be allowances for adding different libraries in the future
    for vf in config["verilog"]:
        v += "verilog work \"%s\"%s" % (vf, os.linesep)

    #print "project file:\n%s" % v
    fp.write(v)
    fp.close()

def get_report_filename(config):
    """
    get the output filename for the project

    Args:
        config (dictionary): configuration dictionary

    Return:
        Nothing

    Raises:
        Nothing
    """
    xst_abs_dir = create_xst_dir(config)
    top_module = config["top_module"]
    output_file = os.path.join(xst_abs_dir, "%s.syr" % top_module)
    return output_file

def get_xst_filename(config, absolute = False):
    """get the output filename"""
    xst_dir = get_xst_dir(config, absolute)
    top_module = config["top_module"]
    xst_file = os.path.join(xst_dir, "%s.xst" % top_module)
    #print "xst filename: %s" % xst_file
    return xst_file

def get_ngc_filename(config, absolute = False):
    """get the output filename"""
    xst_dir = get_xst_dir(config, absolute)
    top_module = config["top_module"]
    ngc_file = os.path.join(xst_dir, "%s.ngc" % top_module)
    #print "xst filename: %s" % xst_file
    return ngc_file

def create_lso_file(config):
    """
    Creates a library search order file location for the XST script

    This is to declutter the base directory

    Args:
        config (dictionary): configuraiton dictionary

    Return:
        Nothing

    Raises:
        (string) relative lso file name
        
    """
    xst_dir = os.path.join(config["build_dir"], XST_DIR)
    lso_fn = os.path.join(xst_dir, XST_PROJECT_LSO)

    xst_abs_dir = create_xst_dir(config)
    fn = os.path.join(xst_abs_dir, XST_PROJECT_LSO)
    #print "lSO filename: %s" % fn
    fp = open(fn, "w")
    #fp.write("DEFAULT_SEARCH_ORDER%s" % os.linesep)
    fp.write("work%s" % os.linesep)
    fp.close()
    
    return lso_fn
    #return fn

def create_xst_script(config):
    """
    given the configuration file create a script that will
    build the verilog files declared within the configuration file

    Args:
        config (dictionary): configuraiton dictionary

    Return:
        (string) script file name

    Raises:
        Nothing
    """
    xst_abs_dir = create_xst_dir(config)
    flags = get_xst_flags(config)
    #print "Flags: %s" % str(flags)

    xst_dir = os.path.join(config["build_dir"], XST_DIR)
    temp_dir = create_temp_dir(config)
    project_dir = os.path.join(xst_dir, PROJECT_FILENAME)

    top_module = config["top_module"]

    output_file = os.path.join(xst_dir, top_module)

    xst_script_fn = os.path.join(xst_abs_dir, XST_SCRIPT_FILENAME)

    fp = open(xst_script_fn, "w")
    fp.write("set -tmpdir \"%s\"%s" % (temp_dir, os.linesep))
    fp.write("set -xsthdpdir \"%s\"%s" % (xst_dir, os.linesep))
    #fp.write("set -xsthdpini \"%s\"%s" % (xst_dir, os.linesep))
    fp.write("run%s" % os.linesep)
    fp.write("-ifn %s%s" % (project_dir, os.linesep))
    fp.write("-ofn %s%s" % (output_file, os.linesep))
    fp.write("-ofmt NGC%s" % (os.linesep))
    fp.write("-p %s%s" % (config["device"], os.linesep))
    fp.write("-top %s%s" % (top_module, os.linesep))
    coregen_files = coregen_utils.get_target_files(config)
    if len(coregen_files) > 0:
        fp.write("-sd %s%s" % (coregen_utils.get_coregen_dir(config, absolute = True), os.linesep))


    #print "flags[lso] = %s" % str(flags["-lso"]["value"])
    if ("-lso" not in flags.keys()) or (len(flags["-lso"]["value"]) == 0):
        #print "creating custom lso file"
        flags["-lso"]["value"] = create_lso_file(config)

    for flag in flags:
        if len(flags[flag]["value"]) == 0:
            continue
        #print "flag: %s: %s" % (flag, flags[flag]["value"])
        fp.write("%s %s%s" % (flag, flags[flag]["value"], os.linesep))

    fp.close()
    return xst_script_fn
