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
import glob
import json

import utils
import coregen_utils

NGD_DEFAULT_FLAG_FILE = "ngd_default_flags.json"
NGD_PROJECT_UCF = "project.ucf"
NGD_DIR = "ngd"

def get_ngd_flags(config):
    """
    Given a configuration dictionary return flags for the NGD build
    if user flags are not specified take the default flags from

    site_scons/ngd_default_flags.json

    Args:
        config (dictionary): configuration dictionary

    Return:
        (dictionary): flag dictionary

    Raises:
        Nothing
    """
    #print "Apply slave tags"
    flags = {}
    user_flags = {}
    if "ngd" in config.keys():
        if "flags" in config["ngd"].keys():
            user_flags = config["ngd"]["flags"]

    fn = os.path.join(os.path.dirname(__file__), NGD_DEFAULT_FLAG_FILE)

    default_flags = json.load(open(fn, "r"))
    default_flags["-dd"]["value"] = get_ngd_dir(config)
    default_flags["-p"]["value"] = config["device"]
    default_flags["-uc"]["value"] = create_ucf_filename(config)
    coregen_files = coregen_utils.get_target_files(config)
    if len(coregen_files) > 0:
        default_flags["-sd"]["value"] = coregen_utils.get_coregen_dir(config, absolute = True)


    for key in default_flags:
        flags[key] = default_flags[key]
        if key in user_flags.keys():
            flags[key]["value"] = user_flags[key]
    return flags

def create_ngd_dir(config):
    """
    Create an ngd directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): ngd output directory (relative)

    Raises:
        Nothing
    """
    #Create a output directory if it does not exist
    build_dir = utils.create_build_directory(config)
    #Now I have an output directory to put stuff in
    #Create an XST directory to put stuff related to XST
    ngd_dir = os.path.join(build_dir, NGD_DIR)
    if not os.path.exists(ngd_dir):
        os.makedirs(ngd_dir)
    return ngd_dir

def get_ngd_dir(config, absolute = False):
    """Returns the ngd output directory location

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
    ngd_dir = os.path.join(build_dir, NGD_DIR)
    return ngd_dir

def get_ngd_filename(config, absolute = False):
    """get the output filename"""
    ngd_dir = get_ngd_dir(config, absolute)
    top_module = config["top_module"]
    ngd_file = os.path.join(ngd_dir, "%s.ngd" % top_module)
    #print "ngd filename: %s" % ngd_file
    return ngd_file

def create_ucf_filename(config):
    """
    find all UCF files assoicated with this project

    this function searches through the constraints directory for any UCF file.

    Unfortunately ngdbuild will only read in one ucf file, so in order to
    include all ucf files the function will aggragate all ucf file to one ucf
    file in the build/ngd/project.ucf file

    Args:
        config (dictionary): configuration dictionary

    Returns:
        (string): file name (absolute) of combinded ucf files

    Raises:
        Nothing
    """
    project_dir = utils.get_project_base()
    #XXX: I should look at the constraints assoicated with coregened files
    ucf_search_path = os.path.join(project_dir, "constraints", "*.ucf")
    ucf_files = glob.glob(ucf_search_path)
    #print "ucf files: %s" % str(ucf_files)
    #Get all ucf files within the cores directory
    #XXX: Need to make an output cores directory

    ngd_dir = get_ngd_dir(config, absolute = True)
    p_ucf_fn = os.path.join(ngd_dir, NGD_PROJECT_UCF)
    fp = open(p_ucf_fn, "w")
    for f in ucf_files:
        ufp = open(f, "r")
        ucf = ufp.read()
        #print "ucf: %s" % ucf
        fp.write(ucf)
        fp.write(os.linesep)
    
    fp.close()
    return p_ucf_fn

def get_ucf_filename(config):
    """Return the name of the project ucf file"""
    ngd_dir = get_ngd_dir(config, absolute = True)
    p_ucf_fn = os.path.join(ngd_dir, NGD_PROJECT_UCF)
    return p_ucf_fn
    
def _get_ucf_files(path):
    """recursively search for ucf files"""
    ucf_files = []
    for base, dirs, _ in os.walk(path):
        for d in dirs:
            p = os.path.join(base, d)
            ucf_files.extend(_get_ucf_files(p))

    search_path = os.path.join(path, '*.ucf')
    ucfs = glob.glob(search_path)
    ucf_files.extend(ucfs)
    return ucf_files



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
    flags = get_ngd_flags(config)
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

