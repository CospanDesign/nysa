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
import re
import json
import glob

import utils

COREGEN_DEFAULT_FOLDER = "cores"
COREGEN_DIR = "cores"
COREGEN_TEMP_DIR = "temp"
COREGEN_TEMPLATE = "coregen_template.json"
COREGEN_PROJECT_NAME = "project.cgp"

def create_coregen_dir(config):
    """
    Create a coregen directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): bitgen output directory (relative)

    Raises:
        Nothing

    """
    core_dir = get_coregen_dir(config, absolute = True)
    if not os.path.exists(core_dir):
        os.makedirs(core_dir)
    return core_dir

def get_coregen_dir(config, absolute = False):
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
    core_dir = os.path.join(build_dir, COREGEN_DIR)
    return core_dir

def create_coregen_temp_dir(config):
    """
    Create a temporary coregen directory in the build folder

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): bitgen output directory (relative)

    Raises:
        Nothing

    """
    temp_dir = get_coregen_temp_dir(config, True)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    return temp_dir

def get_coregen_temp_dir(config, absolute = False):
    """Returns the temporary coregen directory location

    Args:
        config (dictionary): configuration dictionary
        absolute (boolean):
            False (default): Relative to project base
            True: Absolute

    Return:
        (string): string representation of the path to the output

    Raises:
        Nothing
    """
    build_dir = utils.get_build_directory(config, absolute)
    temp_dir = os.path.join(build_dir, COREGEN_DIR, COREGEN_TEMP_DIR)
    return temp_dir

def get_new_coregen_file_list(config):
    """
    Get a list of .xco files from for cores directory

    Args:
        config (dictionary): configuration dictionary

    Return:
        (list of strings): list of filenames

    Raises:
        Nothing
    """
    project_dir = utils.get_project_base()
    core_dir = os.path.join(project_dir, "cores")
    search_path = os.path.join(core_dir, "*.xco")
    files = glob.glob(search_path)
    return files

def customize_all_cores(config, coregen_list):
    """
    Go through each core and customize it for this architecture and apply the
    tags to customize the project

    Args:
        config (dictionary): configuration dictionary

    Returns:
        (list of strings): filenames for the outputted core files

    Raises: Nothing
    """
    new_cores = get_new_coregen_file_list(config)
    for core_filename in new_cores:
        #print "core_filename: %s" % core_filename
        customize_core(config, core_filename)

    return get_customize_core_list(config)

def get_customize_core_list(config):
    """
    Get a list of customized .xco files from the output cores directory

    Args:
        config (dictionary): configuration dictionary

    Returns:
        (list of strings): filenames for the outputted core files

    Raises:
        Nothing
    """
    core_dir = get_coregen_dir(config, absolute = True)
    search_path = os.path.join(core_dir, "*.xco")
    return search_path

def get_target_files(config):
    """
    Return a list filenames for the ngc files created

    Args:
        config (dictionary): configuration dictionary

    Returns:
        (list of strings): filenames for the outputted NGC files
    """
    xco_files = get_new_coregen_file_list(config)
    cd = get_coregen_dir(config, absolute = True)
    files = []
    for f in xco_files:
        of = os.path.splitext(f)[0]
        of = os.path.split(of)[1]
        of = ("%s.ngc" % of)
        of = os.path.join(cd, of)
        files.append(of)
    return files

def create_project_file(config):
    """
    Creates a coregen project with settings for this device

    Args:
        config (dictionary): configuration dictionary

    Returns:
        (string): filename to the project file

    Raises:
        Nothing
    """
    core_dir = get_coregen_dir(config, absolute = True)
    cp_fn = os.path.join(core_dir, COREGEN_PROJECT_NAME)
    fp = open(cp_fn, "w")

    #Open up the template dictionary
    fn = COREGEN_TEMPLATE
    fn = os.path.join(os.path.dirname(__file__), fn)

    template = json.load(open(fn, "r"))

    template["device"] = utils.get_device(config)
    template["devicefamily"] = utils.get_family(config)
    template["package"] = utils.get_package(config)
    template["speedgrade"] = utils.get_speed_grade(config)
    template["workingdirectory"] = get_coregen_temp_dir(config, absolute = True)
    for t in template:
        fp.write("SET %s = %s%s" % (t, template[t], os.linesep))
    fp.close()

    return cp_fn

def get_project_file(config, absolute = False):
    """
    Returns the path to the coregen project

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string): path to project.cgp

    Raises:
        Nothing
    """
    core_dir = get_coregen_dir(config, absolute)
    cp_fn = os.path.join(core_dir, COREGEN_PROJECT_NAME)
    return cp_fn


def customize_core(config, coregen_filename):
    """
    Reads in the xco from the the core directory and customize it for this
    Architecture

    Args:
        config (dictionary): configuration dictionary
        coregen_filename (string): filename of the coregen file to work on

    Returns:
        (string): filename to the custom core path

    Raises:
        Nothing
    """
    #Open the coregen file
    fp = open(coregen_filename)
    core_in = fp.read()
    fp.close()

    #open a reference to the output file
    c_fn = os.path.split(coregen_filename)[1]
    c_fn = os.path.join(get_coregen_dir(config, absolute = True), c_fn)

    #Open up the template dictionary
    fn = COREGEN_TEMPLATE
    fn = os.path.join(os.path.dirname(__file__), fn)

    template = json.load(open(fn, "r"))

    template["device"] = utils.get_device(config)
    template["devicefamily"] = utils.get_family(config)
    template["package"] = utils.get_package(config)
    template["speedgrade"] = utils.get_speed_grade(config)
    template["workingdirectory"] = get_coregen_temp_dir(config, absolute = True)

    #print "Open: %s" % c_fn
    fp = open(c_fn, "w")

    #Break this into lines
    core_in_lines = core_in.splitlines()
    for line in core_in_lines:
        line = line.strip()

        if re.search('BEGIN.*Project.*Options', line, re.I):
            #print "\tFound the beginning of the project"
            fp.write("%s%s" % (line, os.linesep))
            #Copy all the objects into the new file
            for key in template:
                fp.write("SET %s = %s%s" % (key, template[key], os.linesep))

            continue

        if "CRC" in line:
            #Don't write the CRC
            continue

        #if line.startswith("#"):

        #print "line: %s" % line
        items = line.split(' ')
        if "set" == items[0].lower():
            #print "Line: %s" % line
            #Now we have a line we might need to modify
            if items[1].lower() in template.keys():
                #Skip it, cause we already wrote what we wanted into the new xco
                continue

        fp.write("%s%s" % (line, os.linesep))

    fp.close()

