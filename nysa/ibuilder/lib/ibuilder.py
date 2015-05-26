#Distributed under the MIT licesnse.
#Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

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

"""Generates FPGA Projects

This class is used to generate projects given a configuration file
"""

"""Changes:
    06/07/2012:
        -Added Documentation and licsense
    07/17/2013:
        -Cleaning up code

"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
import shutil
import json
from collections import OrderedDict

import utils
import arbiter
from module_processor import ModuleProcessor
from ibuilder_error import ModuleFactoryError
from ibuilder_error import ProjectGeneratorError as PGE

sys.path.append(os.path.join(os.path.dirname(__file__),
                             os.path.pardir,
                             os.path.pardir))

from common import site_manager
from common import status


def get_project_tags(config_filename):
    f = open(config_filename, "r")
    tags = json.load(f, object_pairs_hook = OrderedDict)
    f.close()
    return tags

def get_output_dir(config_filename, debug = False):
    tags = get_project_tags(config_filename)
    return utils.resolve_path(tags["BASE_DIR"])

def generate_project(filename, user_paths = [], output_directory = None, status = None):
    """Generate a FPGA project

    The type of phroject is specific to the vendor called. For example, if the
    configuration file specified that the vendor is Xilinx then the generated
    project would be a PlanAhead project

    Args:
      filename: Name of the configuration file to be read
      user_paths: Paths used to search for modules
      output_directory: Path to override default output directory

    Returns:
      A result of success or fail
        True = Success
        False = Fail

    Raises:
      IOError: An error in project generation has occured
    """
    tags = get_project_tags(filename)

    if not utils.board_exists(tags["board"]):
        utils.install_remote_board_package(tags["board"], status = status)

    utils.clean_verilog_package_paths()
    if len(utils.get_local_verilog_paths()) == 0:
        utils.update_verilog_package()

    pg = ProjectGenerator(user_paths, status = status)
    result = pg.generate_project(filename, output_directory = output_directory)
    return result

def get_parent_board_paths(board_dict):
    paths = []
    if "parent_board" not in board_dict:
        return

    for parent in board_dict["parent_board"]:
        bd = utils.get_board_config(parent)
        if "paths" in bd:
            paths.extend(bd["paths"])
        paths.append(utils.get_board_directory(parent))
        if "parent_board" in bd:
            paths.extend(get_parent_board_paths(bd))

    return list(set(paths))


class ProjectGenerator(object):
    """Generates IBuilder Projects"""

    def __init__(self, user_paths = [], status = None):
        self.user_paths = user_paths
        self.filegen = ModuleProcessor(user_paths = self.user_paths)
        self.project_tags = {}
        self.template_tags = {}
        self.s = status

    def _get_default_board_config(self, board):
        path = os.path.join(utils.get_board_directory(board), board)
        bd = utils.get_board_config(board)
        name = "default.json"
        if "default_project" in bd:
            name = bd["default_project"]

        default_path = os.path.join(path, "board", name)
        #print "Path: %s" % default_path

        board_dict = json.load(open(default_path, "r"), object_pairs_hook=OrderedDict)
        if "parent_board" in bd:
            for parent in bd["parent_board"]:
                pd = utils.get_board_config(parent)
                name = "default.json"
                if "default_project" in pd:
                    name = pd["default_project"]

                path = os.path.join(utils.get_board_directory(parent), parent)
                default_path = os.path.join(path, "board", name)
                parent_dict = json.load(open(default_path, "r"), object_pairs_hook=OrderedDict)

                for key in parent_dict:
                    if self.s: self.s.Verbose("Working on %s key: %s" % (parent, key))
                    if key in board_dict:
                        if isinstance(board_dict[key], list):
                            #print "board_dict  [%s]: %s" % (key, str(board_dict[key]))
                            #print "parent_dict [%s]: %s" % (key, str(parent_dict[key]))
                            l = parent_dict[key] + board_dict[key]
                            #print "L: %s" % l
                            #Remove duplicates
                            board_dict[key] = list(set(l))
                    else:
                        board_dict[key] = parent_dict[key]
        #print "board dict: %s" % str(board_dict)
        return board_dict

    def read_config_file(self, filename="", debug=False):
        """Read in a configuration file name and create a class dictionary

        Args:
          filename: the filename of the configuration file to read in

        Return:
          Nothing

        Raises:
          TypeError
        """
        #try:
        if self.s: self.s.Verbose("Reading configuration file: %s" % filename)
        self.project_tags = json.load(open(filename, "r"), object_pairs_hook=OrderedDict)
        path = os.path.join(utils.get_board_directory(self.project_tags["board"]), self.project_tags["board"])
        board_dict = self._get_default_board_config(self.project_tags["board"])

        #default_path = os.path.join(path, "board", "default.json")
        #board_dict = json.load(open(default_path, "r"), object_pairs_hook=OrderedDict)
        for key in board_dict:
            #print "key: %s" % key
            if key not in self.project_tags:
                if self.s: self.s.Important("Injecting default board key (%s) into project configuration" % key)
                self.project_tags[key] = board_dict[key]
        #except IOError as err:
        #    if self.s: self.s.Fatal("Error while loadng the project tags: %s" % str(err))
        #    raise PGE("Error while loadng the project tags: %s" % str(err))
        #except TypeError as err:
        #    if self.s: self.s.Fatal("Error reading the tags in the project file: %s" % str(err))
        #    raise PGE("Error reading the tags in the project file: %s" % str(err))

    def read_template_file(self, filename, debug=False):
        """Attemp to read in template file

        If we can't find the template file immediately then search for it in
        the default template directory, if it's not there raise an Error

        Args:
            filename (string): Path to the template file

        Return:
            Nothing

        Raises:
            ProjectGeneratorError:
                Unable to find the template.json file
                Error while loading the template.json file
        """
        if not filename.endswith(".json"):
            filename = "%s.json" % filename
        if not os.path.exists(filename):
            test_path = os.path.join(utils.get_nysa_base(),
                                    "ibuilder",
                                    "templates",
                                    filename)
            if os.path.exists(test_path):
                filename = test_path
            else:
                if self.s: self.s.Fatal("Can't find template file at: %s" % (filename))
                raise PGE("Can't find template file at: %s" % (filename))
        try:
            if self.s: self.s.Verbose("Loading template file: %s" % filename)
            self.template_tags = json.load(open(filename, "r"))
        except IOError as err:
            if self.s: self.s.Fatal("Error while loading the template tags: %s" % str(err))
            raise PGE("Error while loading the template tags: %s" % str(err))
        except TypeError as err:
            if self.s: self.s.Fatal("Error reading the tags in the template file: %s" % str(err))
            raise PGE("Error reading the tags in the template file: %s" % str(err))
        except ValueError as err:
            if self.s: self.s.Fatal("Error parsing JSON in template file: %s" % str(err))
            raise PGE("Error parsing JSON in template file: %s" % str(err))

        #Fix all paths to be compatible with the OS and
        #Replace all "${NYSA}" with a
        #print "Replace NYSA name with real paths"
        utils.recursive_dict_name_fix(self.template_tags)

    def generate_project(self, config_filename, output_directory = None):
        """Generate the folders and files for the project

        Using the project tags and template tags this function generates all
        the directories and files of the project. It will go through the template
        structure and determine what files need to be added and call either
        a generation script (in the case of \"top.v\") or simply copy the file
        over (in the case of a peripheral or memory module.

        Args:
          config_filename: name of the JSON configuration file
            output_directory: Path to override default output directory

        Return:
          True: Success
          False: Failure

        Raises:
          TypeError
          IOError
          SapError
        """
        status = self.s
        if status: status.Debug("Openning site manager")

        sm = site_manager.SiteManager()
        path_dicts = sm.get_paths_dict()

        self.read_config_file(config_filename)
        path_dict = sm.get_paths_dict()
        if output_directory is not None:
            self.project_tags["BASE_DIR"] = output_directory

        board_dict = utils.get_board_config(self.project_tags["board"], debug = False)
        cfiles = []
        cpaths = []

        if "paths" in board_dict:
            self.user_paths.extend(board_dict["paths"])
            self.user_paths = list(set(self.user_paths))

        if "parent_board" in board_dict:
            self.user_paths.extend(get_parent_board_paths(board_dict))
            self.user_paths = list(set(self.user_paths))

        # Go through the board dict and see if there is anything that needs to be
        # incorporated into the project tags
        for key in board_dict:
            if key not in self.project_tags:
                self.project_tags[key] = board_dict[key]
            elif isinstance(self.project_tags[key], OrderedDict):
                for k in board_dict[key]:
                    self.project_tags[key][k] = board_dict[key][k]
            elif isinstance(self.project_tags[key], list):
                self.project_tags[key].extend(board_dict[key])
            elif isinstance(self.project_tags[key], dict):
                for k in board_dict[key]:
                    self.project_tags[key][k] = board_dict[key][k]

        self.filegen = ModuleProcessor(user_paths = self.user_paths)

        pt = self.project_tags
        if "constraint_files" not in pt.keys():
            pt["constraint_files"] = []

        cfiles = pt["constraint_files"]
        for c in cfiles:
            cpaths.append(utils.get_constraint_file_path(self.project_tags["board"], c))
            #cpaths.append(utils.get_constraint_file_path(c))

        #if the user didn't specify any constraint files
        #load the default
        if len(cfiles) == 0:
            if status: status.Debug("loading default constraints for: %s" % board_dict["board_name"])
            cfiles = board_dict["default_constraint_files"]
            for c in cfiles:
                cpaths.append(utils.get_constraint_file_path(self.project_tags["board"], c))
                #cpaths.append(utils.get_constraint_file_path(c))


        #extrapolate the bus template
        clock_rate = ""
        if "clockrate" in board_dict:
            if self.s: self.s.Info("User Specified a clockrate of: %d" % board_dict["clockrate"])
            clock_rate = str(board_dict["clockrate"])
        if len(clock_rate) == 0:
            for c in cpaths:
                clock_rate = utils.read_clock_rate(c)
                if len(clock_rate) > 0:
                    #First place I can find the clock rate drop out
                    break

        if len (clock_rate) == 0:
            if self.s: self.s.Fatal("Unable to find the clock rate in any of the constraint"
                      "files: %s" % str(cpaths))
            raise PGE("Unable to find the clock rate in any of the constraint"
                      "files: %s" % str(cpaths))

        #self.project_tags["CLOCK_RATE"] = utils.read_clock_rate(cpaths[0])
        self.project_tags["CLOCK_RATE"] = clock_rate
        self.read_template_file(self.project_tags["TEMPLATE"])

        #set all the tags within the filegen structure
        if status: status.Verbose("set all tags wihin filegen structure")
        self.filegen.set_tags(self.project_tags)

        #generate the project directories and files
        utils.create_dir(self.project_tags["BASE_DIR"])
        if status: status.Verbose("generated project base direcotry: %s" %
            utils.resolve_path(self.project_tags["BASE_DIR"]))

        #generate the arbiter tags, this is important because the top
        #needs the arbiter tags
        arb_tags = arbiter.generate_arbiter_tags(self.project_tags, False)
        self.project_tags["ARBITERS"] = arb_tags

        #print "Parent dir: " + self.project_tags["BASE_DIR"]
        for key in self.template_tags["PROJECT_TEMPLATE"]["files"]:
            self.recursive_structure_generator(
                    self.template_tags["PROJECT_TEMPLATE"]["files"],
                    key,
                    self.project_tags["BASE_DIR"])

        if status: status.Verbose("finished generating project directories")

        if arbiter.is_arbiter_required(self.project_tags):
            if status: status.Verbose("generate the arbiters")
        self.generate_arbiters()

        #Generate all the slaves
        for slave in self.project_tags["SLAVES"]:
            fdict = {"location":""}
            file_dest = os.path.join(self.project_tags["BASE_DIR"], "rtl", "bus", "slave")
            #file_dest = self.project_tags["BASE_DIR"] + "/rtl/bus/slave"
            fn = self.project_tags["SLAVES"][slave]["filename"]
            try:
                self.filegen.process_file(filename = fn, file_dict = fdict, directory=file_dest)
            except ModuleFactoryError as err:
                if status: status.Error("ModuleFactoryError while generating slave: %s" % str(err))
                raise ModuleFactoryError(err)

            slave_dir = os.path.split(utils.find_rtl_file_location(fn, self.user_paths))[0]
            if "constraint_files" in self.project_tags["SLAVES"][slave]:
                temp_paths = self.user_paths
                temp_paths.append(slave_dir)

                for c in self.project_tags["SLAVES"][slave]["constraint_files"]:
                    file_location = utils.get_constraint_file_path(self.project_tags["board"], c, temp_paths)
                    dest_path = utils.resolve_path(self.project_tags["BASE_DIR"])
                    shutil.copy (file_location, os.path.join(dest_path, "constraints", c))

            if "cores" in self.project_tags["SLAVES"][slave]:
                if status: status.Verbose("User Specified an core(s) for a slave")
                for c in self.project_tags["SLAVES"][slave]["cores"]:
                    
                    file_location = os.path.join(slave_dir, os.pardir, "cores", c)
                    if not os.path.exists(file_location):
                        raise PGE("Core: %s does not exist" % file_location)
                    dest_path = utils.resolve_path(self.project_tags["BASE_DIR"])
                    shutil.copy (file_location, os.path.join(dest_path, "cores", c))

            #each slave

        if ("MEMORY" in self.project_tags):
            for mem in self.project_tags["MEMORY"]:
                fdict = {"location":""}
                file_dest = os.path.join(self.project_tags["BASE_DIR"], "rtl", "bus", "slave")
                #file_dest = self.project_tags["BASE_DIR"] + "/rtl/bus/slave"
                fn = self.project_tags["MEMORY"][mem]["filename"]
                try:
                    self.filegen.process_file(filename = fn, file_dict = fdict, directory = file_dest)
                except ModuleFactoryError as err:
                    if status: status.Error("ModuleFactoryError while generating memory: %s" % str(err))
                    raise ModuleFactoryError(err)

        '''
        if 'infrastructure' in self.project_tags:
            if status: status.Verbose("User Specified an infrastructure(s)")
            for entry in self.project_tags["infrastructure"]:
                name = entry.keys()[0]
                im = entry[name]
                path = utils.get_board_directory(name)
                path = os.path.join(path, name, "infrastructure", im["filename"])

                ftdict = {"location":path}
                file_dest = os.path.join(self.project_tags["BASE_DIR"], "rtl", "bus", "infrastructure")
                fn = im["filename"]
                self.filegen.process_file(filename = fn, file_dict = fdict, directory=file_dest)
        '''

        if "cores" in self.project_tags:
            if status: status.Verbose("User Specified an core(s)")
            for entry in self.project_tags["cores"]:
                name = entry.keys()[0]
                for core in entry[name]:
                    file_location = None
                    path = utils.get_board_directory(name)
                    path = os.path.join(path, name, "cores")
                    for root, dirs, files in os.walk(path):
                        if core in files:
                            file_location =  os.path.join(root, core)
                            break
                    if not os.path.exists(file_location):
                        raise PGE("Core: %s does not exist" % file_location)
                    dest_path = utils.resolve_path(self.project_tags["BASE_DIR"])
                    shutil.copy (file_location, os.path.join(dest_path, "cores", core))

        #Copy the user specified constraint files to the constraints directory
        for constraint_fname in cfiles:
            sap_abs_base = os.getenv("SAPLIB_BASE")
            abs_proj_base = utils.resolve_path(self.project_tags["BASE_DIR"])
            constraint_path = utils.get_constraint_file_path(self.project_tags["board"], constraint_fname)
            if os.path.exists(constraint_fname):
                constraint_fname = os.path.split(constraint_fname)[-1]
            #constraint_path = constraint_fname
            if len(constraint_path) == 0:
                print ("Couldn't find constraint: %s, searched in the current directory and %s/hdl/%s" %
                    (constraint_fname, sap_abs_base, self.project_tags["board"]))
                continue
            shutil.copy (constraint_path, os.path.join(abs_proj_base, "constraints", constraint_fname))
            #shutil.copy (constraint_path, abs_proj_base + "/constraints/" + constraint_fname)

        #Generate the IO handler
        interface_filename = self.project_tags["INTERFACE"]["filename"]
        fdict = {"location":""}
        #file_dest = self.project_tags["BASE_DIR"] + "/rtl/bus/interface"
        file_dest = os.path.join(self.project_tags["BASE_DIR"], "rtl", "bus", "interface")
        result = self.filegen.process_file(filename = interface_filename, file_dict=fdict , directory=file_dest)

        if status:
            status.Verbose("verilog files: ")
            for f in self.filegen.verilog_file_list:
                status.Verbose("\t%s" % f)
                #if len(self.filegen.verilog_dependency_list) > 0:
                #    status.Verbose("\t\tdependent files: ")
        if status: status.Verbose("copy over the dependencies...")
        for d in self.filegen.verilog_dependency_list:
            fdict = {"location":""}
            file_dest = os.path.join(self.project_tags["BASE_DIR"], "rtl", "dependencies")
            result = self.filegen.process_file(filename = d, file_dict = fdict, directory = file_dest)
            if status: status.Verbose("\tDependent File: %s" % d)

        return True

    def recursive_structure_generator(self,
                    parent_dict = {},
                    key="",
                    parent_dir = "",
                    debug=False):

        """Recursively generate all directories and files

        Args:
          parent_dict: dictionary of the paret directory
          key: this is the name of the item to add
          parent_dir: name of the parent directory

        Return:
          Nothing

        Raises:
          IOError
          TypeError
        """
        #Check if we are at the base directory

        if (parent_dict[key].has_key("dir") and parent_dict[key]["dir"]):

            #Generating a new Directory

            #Get a path to this new directory
            new_dir = os.path.join(parent_dir, key)
            if (os.path.exists(new_dir)
               and parent_dir is not self.project_tags["BASE_DIR"]):
                #if we are not the base directory and the directory exists,
                #remove it so we are clean there is a check for the base
                #directory because the user might put the project
                #in a pre-existing directory that would be obliterated
                shutil.rmtree(new_dir)

            new_dir = os.path.join(parent_dir, key)
            new_dir = os.path.expanduser(new_dir)

            #Check if there is a key called "recursive_copy", if so copy all
            #remote files here

            if "recursive_copy" in parent_dict[key]:
                #Copy the files from the original directory to the new directory
                orig_dir = parent_dict[key]["recursive_copy"]
                if os.path.exists(new_dir):
                    shutil.rmtree(new_dir)
                shutil.copytree(orig_dir, new_dir)
            else:
                utils.create_dir(os.path.join(parent_dir, key))

            if "files" in parent_dict[key]:
                for sub_key in parent_dict[key]["files"]:
                    #print "sub item :" + sub_key
                    self.recursive_structure_generator(
                        parent_dict = parent_dict[key]["files"],
                        key = sub_key,
                        parent_dir = os.path.join(parent_dir, key))
        else:
            #Generting a new file
            #print "generate the file: " + key + " at: " + parent_dir
            try:
                self.filegen.process_file(key, parent_dict[key], parent_dir)
            except ModuleFactoryError as err:
                print "ModuleFactoryError: %s" % str(err)

    def generate_arbiters(self, debug=False):
        """Generates all the arbiters modules from the configuration file

        Searches for any required arbiters in the configuration file.
        Then generates the required arbiters (2 to 1, 3 to 1, etc...)

        Args:
          Nothing

        Return:
          The largest size arbiter generated (used for testing purposes)

        Raises:
          TypeError
          IOError
        """
        #tags have already been set for this class
        if (not arbiter.is_arbiter_required(self.project_tags, False)):
            return 0
        if self.s: self.s.Debug("Arbiters are required for this project")

        arb_size_list = []
        arbiter_buffer = ""


        #we have some arbiters, add the tag to the project
        #  (this is needed for gen_top)
#        arb_tags = arbiter.generate_arbiter_tags(self.project_tags, False)
#        self.project_tags["ARBITERS"] = arb_tags

        #for each of the items in the arbiter list create a file tags
        #item that can be proecessed by module_processor.process file
        arb_tags = self.project_tags["ARBITERS"]
        for i in range (0, len(arb_tags.keys())):
            key = arb_tags.keys()[i]
            arb_size = len(arb_tags[key]) + 1
            if (arb_size in arb_size_list):
                continue
            if self.s: self.s.Debug("Generating an Arbiter of size: %d" % arb_size)
            #we don't already have this size, so add it into the list
            arb_size_list.append(arb_size)
            fn = "arbiter_" + str(arb_size) + "_masters.v"
            #d = self.project_tags["BASE_DIR"] + "/rtl/bus/arbiters"
            d = os.path.join(self.project_tags["BASE_DIR"], "rtl", "bus", "arbiters")

            self.filegen.buf = arbiter.generate_arbiter_buffer(arb_size)
            if debug: print "arbiter buffer: " + self.filegen.buf
            self.filegen.write_file(d, fn)
        return len(arb_size_list)

