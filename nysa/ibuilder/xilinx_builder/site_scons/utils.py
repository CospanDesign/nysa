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
import platform
import glob
import re


PROJECT_BASE = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), os.pardir))

DEFAULT_CONFIG_FILE = "config.json"
DEFAULT_BUILD_DIR = "build"
TOOL_TYPES=("ise",
            "planahead",
            "vivado")

LINUX_XILINX_DEFAULT_BASE = "/opt/Xilinx"
WINDOWS_XILINX_DEFAULT_BASE = "Xilinx"

class ConfigurationError(Exception):
    """
    Errors associated with configuration:
        getting the configuration file for the project
        getting the default xilinx toolchain
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def get_project_base():
    """
    Returns the project base directory

    Args:
        Nothing

    Returns:
        Path (String) to base directory

    Raises:
        Nothing
    """
    return PROJECT_BASE

def read_config(env):
    """
    Read the build configuration file and creates a dictionary to be used
    throughout the project

    Args:
        env: Environmental variable where the config file is

    Return:
        Dictionary of the configuration

    Raises:
        ConfigurationError
    """

    #Open the configuration file
    fn = env["CONFIG_FILE"]
    if not os.path.exists(fn):
        #if the configuration file name doesn't exists then
        #maybe it is at the base directory of the project
        fn = os.path.join(get_project_base(), fn)


    #if fn == DEFAULT_CONFIG_FILE:
    #    fn = os.path.join(PROJECT_BASE,
    #                      DEFAULT_CONFIG_FILE)
    try:
        config = json.load(open(fn, "r"))
    except TypeError as err:
        raise ConfigurationError(
                "Error parsing json file: %s" % str(err))

    except ValueError as err:
        raise ConfigurationError(
                "Error parsing json file: %s" % str(err))

    except IOError as err:
        raise ConfigurationError(
                "Error openning file: %s: Err: %s" % (fn, str(err)))

    #Return the configuration dicationary
    if "verilog" in config.keys():
        #Fix the verilog paths
        paths = config["verilog"]
        #print "paths: %s" % str(paths)
        vpaths = []
        for vpath in paths:
            #print "vpath: %s" % str(vpath)
            #split the space separaed folders to a
            if "/" in vpath["path"]:
                #Fix linux style paths
                vpath["path"] = vpath["path"].split("/")
            elif "\\" in vpath["path"]:
                #fix windows style paths
                vpath["path"] = vpath["path"].split("\\")
            else:
                vpath["path"] = vpath["path"].split()

            for p in vpath["path"]:
                path = PROJECT_BASE
                #Detect if user gave an actual (absolute) path or a relative path
                if not os.path.isabs(p):
                    #User gave a relative path name
                    path = os.path.join(path, p)

            #print "working path: %s" % path

            if not os.path.exists(path):
                raise ConfigurationError(
                        "Verilog path: (%s) " \
                        "doesn't point to an actual directory or file" % path)

            #if this is a file just append it to vpath
            if os.path.isfile(path):
                #print "Found a file: %s" % path
                if path not in vpaths:
                    vpaths.append(path)

            #this is a directory so now I need to see if this is a recursive
            #directory
            if "recursive" in vpath.keys() and vpath["recursive"]:
                #print "Recursively retreiving files"
                vfs = _get_vfiles(path)
                #print "List of verilog files: %s" % str(vfs)
                for vf in vfs:
                    if vf not in vpaths:
                        vpaths.append(vf)
            else:
                #print "Found a directory: %s" % path
                search_pattern = os.path.join(path, "*.v")
                vfs = glob.glob(search_pattern)
                #print "Found files: %s" % str(vfs)
                vpaths.extend(vfs)

        config["verilog"] = vpaths

    #Check to see if the XST flags exists
    if "xst" not in config.keys():
        config["xst"] = {}
    if "flags" not in config["xst"]:
        config["xst"]["flags"] = {}

    #Check to see if the NGD flags exist
    if "ngd" not in config.keys():
        config["ngd"] = {}
    if "flags" not in config["ngd"]:
        config["ngd"]["flags"] = {}

    return config

def _get_vfiles(path):
    """Recursive inner loop"""
    #print "get recursive files for: %s" % str(path)
    file_path = []
    #dirname, dirs, fs = os.walk(path)
    for base, dirs, _ in os.walk(path):
        for d in dirs:
            p = os.path.join(base, d)
            #print "dir: %s" % p
            file_path.extend(_get_vfiles(p))

    search_path = os.path.join(path, "*.v")
    p = glob.glob(search_path)
    file_path.extend(p)
    return file_path
    

def get_xilinx_tool_types():
    """
    Returns a tuple of the xilinx build tool types

    Args:
        Nothing

    Returns:
        Tuple of build tools (string)

    Raises:
        Nothing
    """
    return TOOL_TYPES

def is_64_bit():
    """
    Returns true if the machine is 64 bits, false if 32 bits

    Args:
        Nothing

    Returns:
        Boolean:
            True: 64 bits
            False: 32 bits

    Raises:
        Nothing
    """
    return platform.machine().endswith('64')

def get_window_drives():
    """
    Returns a list of drives for a windows box

    Args:
        Nothing

    Return:
        Returns a list of drives in a list
    """
    if os.name != "nt":
        raise ConfigurationError("Not a windows box")

    import string
    from ctypes import windll

    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        #For every letter of the alphabet (string.uppercase)
        if bitmask & 1:
            #if the associated bit for that letter is set
            drives.append(letter)
        bitmask >>= 1

    return drives

def find_license_dir(path = ""):
    """
    Based on the operating system attempt to find the license in the default
    locations

    Args:
        path (string): a path to the license, or a path to start searching
            for the license

    Returns:
        (string) A path to where the license files are

    Raises:
        Configuration Error when a license cannot be found
    """
    if len (path) > 0:
        if os.path.exists(path):
            return path

    if os.name == "posix":
        #First attemp to find the file in the default location

        home = os.environ["HOME"]
        xilinx_dir = os.path.join(home, ".Xilinx")
        if os.path.exists(xilinx_dir):
            search_path = os.path.join(xilinx_dir, "*.lic")
            results = glob.glob(search_path)
            if len(search_path) > 0:
                #print "Found directory: %s, results: %s" % (xilinx_dir, str(results[0]))
                return search_path

        raise ConfiugrationError("Error unable to find Xilinx Lincense File")

    elif os.name == "nt":

        print "Windows box... TODO :("
        raise ConfiugrationError("Error unable to find Xilinx Lincense File on Windows box")


def find_xilinx_path(path = "", build_tool = "ISE", version_number = ""):
    """
    Finds the path of the xilinx build tool specified by the user

    Args:
        path (string): a path to the base directory of xilinx
            (leave empty to use the default location)
        build_type (string): to use, valid build types are found with
            get_xilinx_tool_types
            (leave empty for "ISE")
        version_number (string): specify a version number to use
            for one of the tool chain: EG
                build_tool = ISE version_number     = 13.2
                build_tool = Vivado version_number  = 2013.1
            (leave empty for the latest version)


    Returns:
        A path to the build tool, None if not found

    Raises:
        Configuration Error
    """

    #Searches for the xilinx tool in the default locations in Linux and windows
    if build_tool.lower() not in TOOL_TYPES:
        raise ConfigurationError("Build tool: (%s) not recognized \
                                  the following build tools are valid: %s" %
                                  (build_tool, str(TOOL_TYPES)))

    xilinx_base = ""
    if os.name == "posix":
        #Linux
        if len(path) > 0:
            xilinx_base = path
        else:
            xilinx_base = LINUX_XILINX_DEFAULT_BASE
            #print "linux base: %s" % xilinx_base

        #if not os.path.exists(xilinx_base):
        if not os.path.exists(xilinx_base):
            #print "path (%s) does not exists" % LINUX_XILINX_DEFAULT_BASE
            return None

    elif os.name == "nt":
        if path is not None and len(path) > 0:
            xilinx_base = path
        else:
            #Windows
            drives = get_window_drives()
            for drive in drives:
                print "Drive: %s" % str(drive)
                #Check each base directory
                try:
                    dirnames = os.listdir("%s:" % drive)
                    #if WINDOWS_XILINX_DEFAULT_BASE in dirnames:

                    xpath = os.path.join
                    xilinx_base = os.path.join("%s:" % drive,
                            os.path.sep,
                            WINDOWS_XILINX_DEFAULT_BASE)
                    print "Checking: %s" % xilinx_base
                    if os.path.exists(xilinx_base):
                        print "Found: %s" % xilinx_base
                        #this doesn't exists
                        break
                    #Found the first occurance of Xilinx drop out


                except WindowsError, err:
                    #This drive is not usable
                    pass

        if len(xilinx_base) == 0:
                return None

    #Found the Xilinx base
    dirnames = os.listdir(xilinx_base)

    if build_tool.lower() == "ise" or build_tool.lower() == "planahead":
        "ISE and Plan Ahead"
        if len(version_number) > 0:
            if version_number not in dirnames:
                raise ConfigurationError(
                        "Version number: %s not found in %s" %
                        (version_number, xilinx_base))
            return os.path.join(xilinx_base, version_number, "ISE_DS")

        #get the ISE/planahead base
        f = -1.0
        max_float_dir = ""
        for fdir in os.listdir(xilinx_base):
            #print "fdir: %s" % fdir
            try:
                if f < float(fdir):
                    f = float(fdir)
                    #print "Found a float: %f" % f
                    max_float_dir = fdir
            except ValueError, err:
                #Not a valid numeric directory
                pass
        return os.path.join(xilinx_base, max_float_dir, "ISE_DS")

    else:
        if "Vivado" not in dirnames:
            raise ConfigurationError(
                    "Vivado is not in the xilinx directory")

        xilinx_base = os.path.join(xilinx_base, "Vivado")

        if len(os.listdir(xilinx_base)) == 0:
            raise ConfigurationError(
                    "Vivado directory is empty!")

        if len(version_number) > 0:
            if version_number in os.listdir(xilinx_base):
                xilinx_base = os.path.join(xilinx_base, version_number)
                return xilinx_base

        float_max = float(os.listdir(xilinx_base)[0])
        for f in os.listdir(xilinx_base):
            if float(f) > float_max:
                float_max = float(f)

        xilinx_base = os.path.join(xilinx_base, str(float_max))
        return xilinx_base


def create_build_directory(config):
    """
    Reads in a config dictionary and creates a output build directory

    Args:
        config: Config dictionary

    Return:
        Nothing

    Raises:
        Nothing
    """
    build_dir = DEFAULT_BUILD_DIR
    if "build_dir" in config.keys():
        build_dir = config["build_dir"]

    build_dir = os.path.join(get_project_base(), build_dir)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    return build_dir

def get_build_directory(config, absolute = False):
    """Returns the project output directory location

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
    build_dir = DEFAULT_BUILD_DIR
    if "build_dir" in config.keys():
        build_dir = config["build_dir"]

    if absolute:
        build_dir = os.path.join(get_project_base(), build_dir)

    return build_dir

def get_device(config):
    """ Return the device portion of the part
    
    Device portion of an example:

    xc6slx9-tqg144-3: xc6slx9

    Args:
        config (dictionary): configuration dictionary

    Return:
        (string) device

    Raises:
        Nothing
    """
    part_string = config["device"]
    device = part_string.split("-")[0]
    return device.strip()

def get_family(config):
    """
    Returns the family associated with this device
    
    Args:
        config (dictionary): configuration dictionary

    Return:
        (string) device

    Raises:
        Nothing

    """
    #get the device because the family is within there
    device = get_device(config)
    #get the substring of the device string that indicates the family
    if re.search("..32.*an$", device, re.I):
        return "spartan3a"
    if re.search("..3s.*A$", device, re.I):
        return "spartan3a"
    if re.search("..3s.*E$", device, re.I):
        return "spartan3e"
    if re.search("..32.*[0-9]$", device, re.I):
        return "spartan3"
    if re.search("..6s", device, re.I):
        return "spartan6"
    if re.search("..4v", device, re.I):
        return "virtex4"
    if re.search("..5v", device, re.I):
        return "virtex5"
    if re.search("..6v", device, re.I):
        return "virtex6"
    if re.search("..7v", device, re.I):
        return "virtex7"
    if re.search("..7k", device, re.I):
        return "kintex7"
    if re.search("..7a", device, re.I):
        return "artix7"
    raise ConfigurationError("Device Not Found")

def get_speed_grade(config):
    """
    Returns the speed associated with this device
    
    Args:
        config (dictionary): configuration dictionary

    Return:
        (string) speed code (-1, -2, -3, -1L, etc...)

    Raises:
        Nothing

    """

    #split the device value with "-" and get the last value
    #add the '-' back on when it is returned
    speed = config["device"].split("-")[-1]
    speed = speed.strip()
    speed = "-%s" % speed
    return speed

def get_package(config):
    """
    Returns the package associated with this device
    
    Args:
        config (dictionary): configuration dictionary

    Return:
        (string) package

    Raises:
        Nothing

    """

    #split the device string with "-" and get the second value
    package = config["device"].split("-")[1]
    package = package.strip()
    return package

