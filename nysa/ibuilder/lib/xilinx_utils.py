import os
import sys
import string
import glob
import json
from ibuilder_error import XilinxToolchainError


"""
Xilinx specific utilities
"""

"""
Changes:
5/21/2012
    -Initial commit
9/8/2013
    -Incorporating scons functions xilinx find algorithm

"""
LINUX_XILINX_DEFAULT_BASE = "/opt/Xilinx"
WINDOWS_XILINX_DEFAULT_BASE = "Xilinx"



LINUX_DEFAULT_SEARCH_PATHS = ["/opt"]
WINDOWS_DEFAULT_SEARCH_PATHS = ["C:\\xilnix", "D:\\xilinx"]

DEFAULT_SEARCH_PATHS = LINUX_DEFAULT_SEARCH_PATHS

if os.name == "nt":
  DEFAULT_SEARCH_PATHS = WINDOWS_DEFAULT_SEARCH_PATHS

elif os.name == "posix":
  DEFAULT_SEARCH_PATHS = LINUX_DEFAULT_SEARCH_PATHS


def get_version_list(base_directory = None, debug=False):
    """
    Returns a list of version of the Xilinx toolchain
 
    if the user does not specify the base_directory
    the default /opt will be used
    """
    versions = []
    base_dirs = []
 
    if base_directory is None:
        base_dirs = [find_xilinx_path()]
    else:
        base_dirs = [base_directory]
 
    for bd in base_dirs:
        if debug:
            print "searching in %s..." % (bd)
        dir_list = glob.glob(os.path.join(bd, "*"))
        dirs = []
        for d in dir_list:
            if "Xilinx" in d:
                dirs = glob.glob(os.path.join(d,"*"))
                for v in dirs:
                    versions.append(float(v.rpartition(os.path.sep)[2]))
                    break
        
        if debug:
            print "versions: " + str(versions)
 
    return versions


def find_xilinx_path(path = "", version_number = ""):
    """
    Finds the path of the xilinx build tool specified by the user

    Args:
        path (string): a path to the base directory of xilinx
            (leave empty to use the default location)
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
    build_tool = "ISE"
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
        if path is not None or len(path) > 0:
            xilinx_base = path
        else:
            #Windows
            drives = get_window_drives()
            for drive in drives:
                #Check each base directory
                try:
                    dirnames = os.listdir("%s:" % drive)
                    if WINDOWS_XLINX_DEFAULT_BASE in dirnames:
                        xilinx_base = os.path.join("%s:" % drive,
                                WINDOWS_XILINX_DEFUALT_BASE)
                        if os.path.exists(xilinx_base):
                            #this doesn't exists
                            continue
                        #Found the first occurance of Xilinx drop out
                        break

                except WindowsError, err:
                    #This drive is not usable
                    pass

        if len(xiilinx_base) == 0:
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


