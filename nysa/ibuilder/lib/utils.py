# Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa.
#       (http://wiki.cospandesign.com/index.php?title=Nysa.org)
#
# Nysa is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Nysa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Nysa; If not, see <http://www.gnu.org/licenses/>.

"""Utilites that are used by all modules."""

"""
Changes:
12/06/2011
    -Modified the clock_read function so that the ucf file can have
    quotation marks
04/22/2012
    -Added the get_slave_list function that returns a list of the
    available slave filenames
05/05/2012 (Cinqo de mayo, Woot!)
    -Added get_net_names to get all the names within a constraint file
05/10/2012
    -Added get_board_config to get all the configuration for a specified board
05/12/2012
    -Added get_board_names to get all the board names
06/07/2012
    -Added documentation and licsense
06/11/2012
    -Moved two functions from sapfile to saputils
        is_module_in_file
        find_module_filename_
07/17/2013
    -Added two new functions:
        create_native_path
        recursive_dict_name_fix
09/08/2013
    -Switched to GPL V3 License because the user can make their code private but
    this tool should always be free
"""


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import string
import glob
import json
import urllib2

import preprocessor
import constraint_utils

from ibuilder_error import ModuleNotFound
from ibuilder_error import NysaEnvironmentError
from ibuilder_error import IBuilderError

nysa_base = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "common")))

import site_manager



def get_nysa_base():
    """Returns the base directory of nysa using the configuration file in the
      the user directory

      Args:
        Nothing

      Returns:
        Absolute directory of the Nysa base directory. This requires the user to
        setup Nysa by running the 'init_settings.py' in the Nysa base directory

      Raises:
        NysaEnvironmentError
    """
    base = os.path.dirname(__file__)
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
    return nysa_base

def get_nysa_user_base():
    """Returns the path to Nysa user base. This is the directory where the user
    generally puts all their files

    Args:
        Nothing

    Returns (String):
        absolute path to the user base directory

    Raises:
        SiteManagerError: Errors associated with site manager
    """
    sm = site_manager.SiteManager()
    return sm.get_nysa_user_base_directory()

def create_dir(dirname, debug=False):
    """Generate a directory with the specified location

    Generate a directory even if the parent directories don't exist

    Args:
      dirname: name of the directory to create
        example: "~/project"

    Returns:
      True = Success
      False = Fail

    Raises:
      os.error: failed to create directory
    """

    if dirname.startswith("~"):
        dirname = os.path.expanduser(dirname)
    if os.path.exists(dirname):
        return
    os.makedirs(dirname)
    return

#XXX: Is there a native function within Python that does this?
def resolve_path(filename):
    """Returns filename with an absolute path.

    Args:
      filename: String of the file, this could be a relative path
        or an absolute path

    Returns:
      A filename with an absolute path

    Raises:
      Nothing
    """
    if filename.startswith("~"):
        filename = os.path.expanduser("~") + filename.strip("~")
    return filename

def remove_comments(buf="", debug=False):
    """Remove comments from a buffer.

    Args:
        buf = Buffer to remove the comments from

    Returns:
        A buffer with no verilog comments in it

    Raises:
        Nothing
    """
    #first pass remove the '//' comments
    lines = buf.splitlines()
    if debug:
        print "buf:\n" + buf
    bufx = ""
    for line in lines:
        line = line.partition("//")[0]
        bufx = bufx + line + "\n"
    if debug:
        print "bufx:\n" + bufx

    if debug:
        print "working on /* */ comments\n\n\n"
    #get rid of /*, */ comments
    buf_part = bufx.partition("/*")
    pre_comment = ""
    post_comment = ""
    bufy = bufx
    while (len(buf_part[1]) != 0):
        pre_comment = buf_part[0]
        post_comment = buf_part[2].partition("*/")[2]
        #print "pre_comment: " + pre_comment
        #print "post comment: " + post_comment
        bufy = pre_comment + post_comment
        buf_part = bufy.partition("/*")
        pre_comment = ""
        post_comment = ""

    if debug:
        print "buf:\n" + bufy

    return bufy

def find_rtl_file_location(filename="", user_paths = [], debug=False):
    """Finds a RTL file in the cbuilder rtl directory.

    Args:
        filename: the name of a verilog file to search for
        user_paths: list of paths to search for cbuilder projects

    Returns:
        If found, The absolute path of the verilog module file,
        Otherwise an empty string

    Raises:
      Nothing
    """
    local_dirs = get_local_verilog_paths()

    for d in local_dirs:
        for root, dirs, names in os.walk(d):
            if filename in names:
                return os.path.join(root, filename)

    if debug: print "Looking in custom path: %s" % user_paths

    for path in user_paths:
        for root, dirs, names in os.walk(path):
            if filename in names:
                return os.path.join(root, filename)

    raise ModuleNotFound("File: %s not found, looked in %s and the default location %s" % (filename, str(user_paths), local_dirs))
#XXX: This should probably return none, and not an empty string upon failure
#XXX:   perhaps even raise an error


def get_board_names (user_paths = [], debug = False):
    """Returns a list of all the board names"""
    sm = site_manager.SiteManager()
    #Get the installed board locations
    boards = sm.get_local_board_names()

    #Check user paths
    board_locations = user_paths
    for bl in board_locations:
        for root, dirs, names in os.walk(bl):
            if debug: print "Dirs: " + str(dirs)
            for bn in dirs:
                boards.append(bn)

    return boards

def get_constraint_filenames (board_name, user_paths = [], debug = False):
    """Returns a list of ucf files for the specified board name"""
    #board_dir = os.path.join(nysa_base, "ibuilder", "boards", board_name)
    sm = site_manager.SiteManager()
    board_location = None
    cfiles = []

    try:
        board_location = get_board_directory(board_name)
        config_dict = get_board_config(board_name, user_paths, debug = debug)
        if "default_constraint_files" in config_dict:
            for cf in config_dict["default_constraint_files"]:
                cfiles.append(os.path.join(board_location, board_name, "board", cf))

    except site_manager.SiteManagerError as ex:
        if debug: print "%s is not in the installed path, checking user paths..." % board_name

    #board_locations = [board_dir]
    #board_locations.extend(user_paths)
    board_locations = user_paths

    for bl in board_locations:
        if debug: print "Board dir: %s" % bl
        for root, dirs, names in os.walk(bl):
            if debug:
                print "names: " + str(names)

            for name in names:
                s = name.partition(".")[2].lower()

                if debug:
                    print "last: " + s
                if s == "ucf":
                    cfiles.append(name)
                    if debug:
                        print "constraint file: %s" % name

    return cfiles

def get_board_config (board_name, user_paths = [], debug = False):
    """Returns a dictionary of board specific information

    Args:
        board_name: the name of the board to get the information from
            Example: \"sycamore1\"

    Returns:
        A dictionary of the board configuration data

    Raises:
        Nothing
    """
    sm = site_manager.SiteManager()
    board_location = None
    bn = str(board_name).lower()
    try:
        board_location = get_board_directory(board_name)
    except site_manager.SiteManagerError as ex:
        if debug: print "%s is not in the installed path, checking user paths..." % board_name
        pass

    if board_location is None:
        board_locations = user_paths

        filename = ""
        buf = ""
        config_dict = {}

        if debug: print "Looking for: " + board_name
        final_path = None

        for bl in board_locations:
            for root, dirs, names in os.walk(bl):
                if debug: print "Dirs: " + str(dirs)
                if board_name in dirs:
                    if debug: print "Found the directory"
                    final_path = os.path.join(root)
                    filename = os.path.join(root, bn, "board", "config.json")
                    if os.path.exists(filename):
                        if debug: print "filename: %s" % filename
                        break

        if len(filename) == 0:
            if debug: print "didn't find board config file"
            return {}

        board_location = final_path

    else:
        filename = os.path.join(board_location, bn, "board", "config.json")

    #open up the config file
    file_in = open(filename)
    buf = file_in.read()
    config_dict = json.loads(buf)
    file_in.close()

    if debug:
        print "Opened up the board config file for %s" % (board_name)

    #Create absolute references to any files within the board config files
    if "default_constraint_files" in config_dict:
        #Create absolute references to any filenames declared
        filenames = config_dict["default_constraint_files"]
        abs_filenames = []
        path = os.path.join(board_location, bn, "board")
        if debug: print "Path: %s" % str(path)
        for filename in filenames:
            if not os.path.exists(filename):
                if ("/" in filename) or ("\\" in filename):
                    path_list = []
                    if "/" in filename:
                        path_list = filename.split("/")
                    else:
                        path_list = filename.split("\\")

                    filename = path
                    for p in path_list:
                        filename = os.path.join(filename, p)
                else:
                    filename = os.path.join(path, filename)

                filename = os.path.abspath(filename)

            abs_filenames.append(filename)

        config_dict["default_constraint_files"] = abs_filenames

    if debug: print "Looking for a parent board"
    if "parent_board" in config_dict:
        if debug: print "Found a reference to parent!"
        for parent in config_dict["parent_board"]:
            if debug: print "Parent: %s" % parent
            parent_config = get_board_config(parent, user_paths, debug = debug)
            for key in parent_config:
                if debug: print "Looking at key: %s" % key
                if key not in config_dict:
                    if debug: print "\tKey not in child dict, inserting..."
                    config_dict[key] = parent_config[key]
                if isinstance(config_dict[key], list):
                    if debug: print "\tFound a list, appending values..."
                    config_dict[key] += parent_config[key]
                    if debug: print "\tNew list: %s" % str(config_dict[key])

            if "required" in parent_config:
                #print "Found a required in config dict"
                filepath = get_board_directory(parent)
                filepath = os.path.join(filepath, parent, "board", parent_config["required"])
                f = open(filepath, 'r')
                required = json.load(f)
                f.close()
                for key in required:
                    #print "Found a required entry: %s" % key
                    if key not in config_dict:
                        config_dict[key] = required[key]
                    elif isinstance(config_dict[key], list):
                        config_dict[key] += required[key]
                    elif isinstance(config_dict[key], dict):
                        for k in required[key]:
                            config_dict[key][k] = parent_config[key][k]
                        
     #for debug
    if "paths" not in config_dict:
        config_dict["paths"] = []
    config_dict["paths"].append(board_location)
    return config_dict

def get_net_names(filepath, debug = False):
    """Gets a list of net in a given constraint file

    Args:
        constrint_filename: name of a constraint file with an absolute path

    Returns:
        A list of constraint for the module
        NOTE: This file fails quietly and shouldn't this needs to be fixed!

    Raises:
        IBuilder Error
    """
    return constraint_utils.get_net_names(filepath)

def get_constraint_file_path(board_name, constraint_filename, user_paths = [], debug = False):
    """Gets the path of the constraint filename

    Args:
        board_name (String): name of the board to get the constraint name
        constraint_filename (String): name of a constraint file to find
        user_paths (String): list of user paths to add to the search directory


    Returns:
        (String) path to the constraint filename

    Raises:
        IBuilder Error
    """
    if os.path.exists(constraint_filename):
        return os.path.abspath(constraint_filename)

    board_name = board_name.lower()
    """Returns a list of ucf files for the specified board name"""
    #board_dir = os.path.join(nysa_base, "ibuilder", "boards", board_name)
    sm = site_manager.SiteManager()
    board_location = None
    board_locations = []

    try:
        board_location = get_board_directory(board_name)
        if debug: print "Default board location found: %s" % board_location
        config_dict = get_board_config(board_name, user_paths, debug = debug)
        if debug: print "Config Dict: %s" % str(config_dict)
        if "default_constraint_files" in config_dict:
            for cf in config_dict["default_constraint_files"]:
                if debug: print "Looking at constraint file: %s" % cf
                if constraint_filename == cf:
                    return os.path.join(board_location, board_name, "board", cf)

    except site_manager.SiteManagerError as ex:
        if debug: print "%s is not in the installed path, checking user paths..." % board_name

    board_locations.extend(user_paths)
    filename = ""
    buf = ""
    clock_rate = ""
    if debug: print "Looking for: " + constraint_filename
    for bl in board_locations:
        for root, dirs, names in os.walk(bl):
            if debug: print "name: " + str(names)
            if constraint_filename in names:
                if debug: print "found the file!"
                return os.path.join(root, constraint_filename)

    if (len(filename) == 0):
        verilog_dirs = get_local_verilog_paths()
        for vd in verilog_dirs:
            for root, dirs, names in os.walk(vd):
                if debug: print "name: " + str(names)
                if constraint_filename in names:
                    if debug: print "found the file: %s" % os.path.join(root, constraint_filename)
                    return os.path.join(root, constraint_filename)

    raise IBuilderError("Constraint File: %s wasn't found, looked in board directories and core directories" % constraint_filename)


def read_clock_rate(constraint_filepath, debug = False):
    """Returns a string of the clock rate

    Searches through the specified constraint file to determine if there
    is a specified clock. If no clock is specified then return 50MHz = 50000000

    Args:
      constraint_filepath: the name of the constraint file to search through

    Returns:
      A string representation of the clock rate
      NOTE: on error this fails quietly this should probably be different

    Raises:
      Nothing
    """
    return constraint_utils.read_clock_rate(constraint_filepath)

def _get_slave_list(directory, debug = False):
    """Gets a list of slaves given a directory"""
    file_list = _get_file_recursively(directory)

    if debug:
        print "verilog files: "
    for f in file_list:
        if debug:
            print "\t" + f

    slave_list = []
    #check to see if the files are a wishbone slave file
    for f in file_list:
        fin = None
        data = ""
        try:
            fin = open(f, "r")
            data = fin.read()
            fin.close()

        #XXX: This should probably allow the calling function to handle a failure
        except IOError as err:
            if debug:
                print "failed to open: " + str(err)
                return None

        if "SDB_NAME" not in data:
            continue

        name = f.split("/")[-1]
        if name == "wishbone_slave_template.v":
            continue

        slave_list.append(f)

    if debug:
        print "slave list: "
        for f in slave_list:
            print "\t" + f

    return slave_list

def get_slave_list(bus = "wishbone", user_paths = [], debug = False):
    """Gets a list of slaves

    Args:
      bus: a string declaring the bus type, this can be
        \"wishbone\" or \"axie\"
      user_cbuider_paths: besides the normal paths to search for, also search
      these paths for cbuilder slave projects

    Returns:
      A list of slaves

    Raises:
      Nothing
    """

    if debug:
        print "in get slave list"
    directory = get_local_verilog_path("nysa-verilog")
    #directory = os.path.join(nysa_base, "cbuilder", "verilog", bus, "slave")
    file_list = _get_file_recursively(directory)
    slave_list = _get_slave_list(directory, debug=debug)
    for path in user_paths:
        #print "utils: Checking: %s" % path
        slave_list += _get_slave_list(path, debug=debug)

    return slave_list


def is_module_in_file(filename, module_name, debug = False):
    fbuf = ""

    try:
        filein = open(filename)
        fbuf = filein.read()
        filein.close()
    except IOError as err:
        if debug:
          print "the file is not a full path, searching RTL"

        try:
            filepath = find_rtl_file_location(filename)
            filein = open(filepath)
            fbuf = filein.read()
            filein.close()
        except IOError as err_int:
            if debug:
                print "%s is not in %s" % (module_name, filename)
            return False

    if debug:
        print "Openning file: %s" % filename

    fbuf = remove_comments(fbuf)
    done = False
    module_string = fbuf.partition("module")[2]

    while (not done):
        #remove the parameter and ports list from this possible module
        module_string = module_string.partition("(")[0]
        module_string = module_string.strip("#")
        module_string = module_string.strip()

        if debug:
            print "Searching through: %s" % module_string

        if len(module_string) == 0:
            if debug:
                print "length of module string == 0"
            done = True

        if module_string.endswith("("):
            if debug:
                print "module_string endswith \"(\""
            module_string = module_string.strip("(")

        if debug:
            print "Looking at: %s" % module_string

        if module_string == module_name:
            #Success!
            if debug:
                print "Found %s in %s" % (module_string, filename)
            return True

        elif len(module_string.partition("module")[2]) > 0:
            if debug:
                print "Found another module in the file"
            module_string = module_string.partition("module")[2]

        else:
            done = True

    return False


def _find_module_filename (directory, module_name, debug = False):
    filename = ""

    verilog_files = []
    #get all the verilog files
    for root, dirs, files in os.walk(directory):
        filelist = [os.path.join(root, fi) for fi in files if fi.endswith(".v")]
        for  f in filelist:
            verilog_files.append(f)

    for f in verilog_files:
        if debug:
            print "serching through %s" % f

        if is_module_in_file(f, module_name):
            while len(f.partition(os.path.sep)[2]):
                f = f.partition(os.path.sep)[2]
            if debug:
                print "Found a file with the name: " + f
            filename = f
            break

    if len(filename) == 0:
        raise ModuleNotFound("Searched in standard hdl/rtl location for file \
            containing the module %s" % module_name)
    return filename

def find_module_filename (module_name, user_paths = [], debug = False):
    cwd = os.getcwd()
    filename = ""
    if debug: print "nysa base: %s" % nysa_base
    #base = os.path.join(nysa_base, "cbuilder", "verilog")
    base = os.path.join(get_local_verilog_path("nysa-verilog"), "verilog")
    paths = [base]
    paths.extend(user_paths)

    if debug: print "Search directory: %s" % str(paths)
    for p in paths:
        try:
            return _find_module_filename(p, module_name, debug = debug)
        except ModuleNotFound as mnf:
            continue

    raise ModuleNotFound ("Module %s not found: Searched in Nysa directory: %s as well as the following directories %s" % (module_name, base , str(user_paths)))


def _get_file_recursively(directory):
    file_dir_list = glob.glob(directory + "/*")
    file_list = []
    for f in file_dir_list:
        if (os.path.isdir(f)):
            if(f.split("/")[-1] != "sim"):
                file_list += _get_file_recursively(f)
        elif (os.path.isfile(f)):
            if f.endswith(".v"):
                file_list.append(f)

    return file_list


def recursive_dict_name_fix(d):
    """
    In order to indicate that we are referencing a path from the Nysa base
    directory the string ${NYSA} is inserted, this was in hopes of using the
    string template function but that doesn't work really well for
    dictionaries so just go through all the dictionary entries and replace
    all the dictionary items with a reference to the base

    Args:
        d: (Dictionary) dictionary or string to fix

    Returns:
        Nothing: (all changes are done in place)

    Raises:
        Nothing
    """
    for key in d:
        #print "key: %s" % key
        #print "type: %s" % str(type(d[key]))
        if isinstance(d[key], str) or isinstance(d[key], unicode):
            #print "key is string"
            path = d[key]
            #print "path: %s" % path
            if "${NYSA}" in path:
                #print "Initial Path: %s" % path
                p = path.partition("${NYSA}")[2]
                p = create_native_path(p)
                p = os.path.join(get_nysa_base(), p)
                d[key] = p
                #print "Final Path: %s" % p
            else:
                d[key] = create_native_path(path)
        elif isinstance(d[key], dict):
            #print "working on a dictionary"
            recursive_dict_name_fix(d[key])


def create_native_path(path):
    """
    All nysa paths are stored in a *nix style, but Nysa may be run on a
    different OS, so Take any path that is pulled in and send it out as a
    native path for this OS

    Args:
        path (string): path to change

    Return:
        (string): native path

    Raises:
        Nothing
    """
    out_path = ""
    units = path.split("/")
    for unit in units:
        out_path = os.path.join(out_path, unit)
    return out_path

def pretty_print_dict(d):
    """
    Prints the given dictionary in a human readible format

    Args:
        d (dictionary): Dictionary to display

    Return:
        Nothing

    Raises:
        Nothing
    """
    print json.dumps(d,
                     sort_keys = True,
                     indent = 2,
                     separators=(',', ':'))

def get_board_directory(board_name):
    return site_manager.SiteManager().get_board_directory(board_name)

def board_exists(board_name):
    sm = site_manager.SiteManager()
    return sm.board_exists(board_name)

def install_remote_board_package(board_name, status = None):
    sm = site_manager.SiteManager()
    s = status
    if s: s.Warning("Could not find %s on local host" % board_name)
    if not sm.remote_board_exists(board_name):
        if s: s.Fatal("Could not find %s in remote board table" % board_name)
        raise PGE("Could not find board %s on local host, checked remote board table" % board_name)

    if s: s.Verbose("Found %s on the remote server" % board_name)

    board_path = os.path.join(site_manager.get_board_package_path(), board_name)
    if s: s.Important("Installing %s to %s" % (board_name, site_manager.get_board_package_path()))
    sm.install_remote_board_package(board_name)

def get_board_id_dict():
    sm = site_manager.SiteManager()
    return sm.get_board_id_dict()

def update_board_id_dict():
    sm = site_manager.SiteManager()
    sm.update_board_id_dict()

def is_board_id_in_dict(name):
    sm = site_manager.SiteManager()
    bid = sm.get_board_id_dict()
    if name not in bid:
        return False
    return True

def get_board_id(name):
    sm = site_manager.SiteManager()
    bid = sm.get_board_id_dict()
    return sm.get_board_id_dict()[name]

def clean_verilog_package_paths():
    sm = site_manager.SiteManager()
    sm.clean_verilog_package_paths()

def get_local_verilog_paths():
    sm = site_manager.SiteManager()
    temp_dirs = sm.get_local_verilog_paths()
    local_dirs = []

    package_names = sm.get_local_verilog_package_names()
    for d in temp_dirs:
        if os.path.exists(os.path.join(d, "verilog")):
            local_dirs.append(os.path.join(d, "verilog"))
        else:
            local_dirs.append(d)

    return local_dirs

def update_verilog_package(name = None, branch = None):
    sm = site_manager.SiteManager()
    sm.update_verilog_package(name, branch)

def get_local_verilog_path(name):
    sm = site_manager.SiteManager()
    package_names = sm.get_local_verilog_package_names()
    if name.lower() not in package_names:
        raise IBuilderError("Verilog package %s not found!", name)
    return sm.get_local_verilog_package_path(name.lower())

def get_local_verilog_path_dict():
    sm = site_manager.SiteManager()
    package_names = sm.get_local_verilog_package_names()
    vpackage_dict = {}
    for pname in package_names:
        vpackage_dict[pname] = sm.get_local_verilog_package_path(pname)

    return vpackage_dict

def try_internet():
    try:
        #Try and get a response from a google server
        response = urllib2.urlopen("http://74.125.22.100", timeout = 1)
        return True
    except:
        pass
    return False

def get_user_project_dir():
    sm = site_manager.SiteManager()
    return sm.get_user_project_dir()

def get_user_examples_dir():
    sm = site_manager.SiteManager()
    return sm.get_user_examples_dir()

def get_user_verilog_dir():
    sm = site_manager.SiteManager()
    return sm.get_user_verilog_dir()

def get_user_app_dir():
    sm = site_manager.SiteManager()
    return sm.get_user_app_dir()

def get_user_dev_dir():
    sm = site_manager.SiteManager()
    return sm.get_user_dev_dir()

def get_user_cbuilder_project_dir():
    sm = site_manager.SiteManager()
    return sm.get_user_cbuilder_project_dir()

def get_user_ibuilder_project_dir():
    sm = site_manager.SiteManager()
    return sm.get_user_ibuilder_project_dir()

