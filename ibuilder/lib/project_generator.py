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

import utils
import arbitor
from module_processor import ModuleProcessor
from ibuilder_error import ModuleFactoryError
from ibuilder_error import ProjectGeneratorError as PGE

class ProjectGenerator:
    """Generates IBuilder Projects"""
 
    def __init__(self, user_paths = []):
        self.user_paths = user_paths
        self.filegen = ModuleProcessor(user_paths = self.user_paths)
        self.project_tags = {}
        self.template_tags = {}
        return

    def read_config_file(self, filename="", debug=False):
        """Read in a configuration file name and create a class dictionary
       
        Args:
          filename: the filename of the configuration file to read in
       
        Return:
          Nothing
       
        Raises:
          TypeError
        """
        try:
            self.project_tags = json.load(open(filename, "r"))
        except IOError as err:
            raise PGE("Error while loadng the project tags: %s" % str(err))
        except TypeError as err:
            raise PGE("Error reading the tags in the project file: %s" % str(err))



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
                raise PGE("Can't find template file at: %s" % (filename))
        try:
            self.template_tags = json.load(open(filename, "r"))
        except IOError as err:
            raise PGE("Error while loading the template tags: %s" % str(err))
        except TypeError as err:
            raise PGE("Error reading the tags in the template file: %s" % str(err))
        except ValueError as err:
            raise PGE("Error parsing JSON in template file: %s" % str(err))

        #Fix all paths to be compatible with the OS and
        #Replace all "${NYSA}" with a 
        print "Replace NYSA name with real paths"
        utils.recursive_dict_name_fix(self.template_tags)

        
    def generate_project(self, config_filename, debug=False):
        """Generate the folders and files for the project
       
        Using the project tags and template tags this function generates all
        the directories and files of the project. It will go through the template
        structure and determine what files need to be added and call either
        a generation script (in the case of \"top.v\") or simply copy the file
        over (in the case of a peripheral or memory module.
       
        Args:
          config_filename: name of the JSON configuration file
       
        Return:
          True: Success
          False: Failure
       
        Raises:
          TypeError
          IOError
          SapError
        """
        self.read_config_file(config_filename)
        board_dict = utils.get_board_config(self.project_tags["board"])
        cfiles = []

        pt = self.project_tags
        if "constraint_files" in pt.keys():
            cfiles = pt["constraint_files"]
        
        #if the user didn't specify any constraint files
        #load the default
        if len(cfiles) == 0:
            if debug: print "board dict: %s" % str(board_dict)
            cfiles = board_dict["default_constraint_files"]
        
        #extrapolate the bus template
#XXX: Need to check all the constraint files
        clock_rate = ""
        for c in cfiles:
            clock_rate = utils.read_clock_rate(c)
            if len(clock_rate) > 0:
                #First place I can find the clock rate drop out
                break
        
        if len (clock_rate) == 0:
            raise PGE("Unable to find the clock rate in any of the constraint"
                      "files: %s" % str(cfiles))

        self.project_tags["CLOCK_RATE"] = utils.read_clock_rate(cfiles[0])
        self.read_template_file(self.project_tags["TEMPLATE"])

        #set all the tags within the filegen structure
        if debug: print "set all tags wihin filegen structure"
        self.filegen.set_tags(self.project_tags)
        
        #generate the project directories and files
        utils.create_dir(self.project_tags["BASE_DIR"])
        if debug: print "generated the first dir"
        
        #generate the arbitor tags, this is important because the top
        #needs the arbitor tags
        arb_tags = arbitor.generate_arbitor_tags(self.project_tags, False)
        self.project_tags["ARBITORS"] = arb_tags
        
        #print "Parent dir: " + self.project_tags["BASE_DIR"]
        for key in self.template_tags["PROJECT_TEMPLATE"]["files"]:
            self.recursive_structure_generator(
                    self.template_tags["PROJECT_TEMPLATE"]["files"],
                    key,
                    self.project_tags["BASE_DIR"])
        
        if debug: print "generating project directories finished"
        
        if debug: print "generate the arbitors"
        self.generate_arbitors()
        
        #Generate all the slaves
        for slave in self.project_tags["SLAVES"]:
            fdict = {"location":""}
            file_dest = self.project_tags["BASE_DIR"] + "/rtl/bus/slave"
            fn = self.project_tags["SLAVES"][slave]["filename"]
            try:
                self.filegen.process_file(filename = fn, file_dict = fdict, directory=file_dest, debug=debug)
            except ModuleFactoryError as err:
                print "ModuleFactoryError while generating a slave: %s" % str(err)
           
            #each slave
 
        if ("MEMORY" in self.project_tags):
            for mem in self.project_tags["MEMORY"]:
                fdict = {"location":""}
                file_dest = self.project_tags["BASE_DIR"] + "/rtl/bus/slave"
                fn = self.project_tags["MEMORY"][mem]["filename"]
                try:
                    self.filegen.process_file(filename = fn, file_dict = fdict, directory = file_dest)
                except ModuleFactoryError as err:
                    print "ModuleFactoryError while generating a memory slave: %s" % str(err)
 
        #Copy the user specified constraint files to the constraints directory
        for constraint_fname in cfiles:
            sap_abs_base = os.getenv("SAPLIB_BASE")
            abs_proj_base = utils.resolve_path(self.project_tags["BASE_DIR"])
            constraint_path = self.get_constraint_path(constraint_fname)
            if len(constraint_path) == 0:
                print ("Couldn't find constraint: %s, searched in the current directory and %s/hdl/%s" %
                    (constraint_fname, sap_abs_base, self.project_tags["board"]))
                continue
            shutil.copy (constraint_path, abs_proj_base + "/constraints/" + constraint_fname)
 
        #Generate the IO handler
        interface_filename = self.project_tags["INTERFACE"]["filename"]
        fdict = {"location":""}
        file_dest = self.project_tags["BASE_DIR"] + "/rtl/bus/interface"
        result = self.filegen.process_file(filename = interface_filename, file_dict=fdict , directory=file_dest)
 
        if debug:
            print "copy over the dependencies..."
            print "verilog files: "
            for f in self.filegen.verilog_file_list:
                print f
                print "dependent files: "
        for d in self.filegen.verilog_dependency_list:
            fdict = {"location":""}
            file_dest = os.path.join(self.project_tags["BASE_DIR"], "rtl", "dependencies")
            result = self.filegen.process_file(filename = d, file_dict = fdict, directory = file_dest)
            if debug: print d
 
        return True

    def get_constraint_path (self, constraint_fname, debug = False):
        """get_constraint_path
       
        given a constraint file name determine where that constraint is
       
        Args:
          constraint_fname: the name of the constraint file to search for
       
        Return:
          path of the constraint
       
        Raises:
          ProjectGeneratorError:
            Can't find the constraint file in the board directory
        """
        board_name  = self.project_tags["board"]

        #Check in this directory
        test_path = os.path.join(os.getcwd(), constraint_fname)
        if os.path.exists(test_path):
            return test_path

        #search through the board directory
        board_dir = os.path.join(utils.get_nysa_base(), "ibuilder", "boards", board_name, constraint_fname)
        if debug: print "Board Dir: %s" % board_dir
        if os.path.exists(board_dir):
            return board_dir
       
        raise IOError ("Path for the constraint file %s not found" % constraint_fname)

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

    def generate_arbitors(self, debug=False):
        """Generates all the arbitors modules from the configuration file
       
        Searches for any required arbitors in the configuration file.
        Then generates the required arbitors (2 to 1, 3 to 1, etc...)
       
        Args:
          Nothing
       
        Return:
          The largest size arbitor generated (used for testing purposes)
       
        Raises:
          TypeError
          IOError
        """
        #tags have already been set for this class
        if (not arbitor.is_arbitor_required(self.project_tags, False)):
            return 0
       
        arb_size_list = []
        arbitor_buffer = ""
       
       
        #we have some arbitors, add the tag to the project
        #  (this is needed for gen_top)
#        arb_tags = arbitor.generate_arbitor_tags(self.project_tags, False)
#        self.project_tags["ARBITORS"] = arb_tags
       
        #for each of the items in the arbitor list create a file tags
        #item that can be proecessed by module_processor.process file
        arb_tags = self.project_tags["ARBITORS"]
        for i in range (0, len(arb_tags.keys())):
            key = arb_tags.keys()[i]
            arb_size = len(arb_tags[key]) + 1
            if (arb_size in arb_size_list):
                continue
            #we don't already have this size, so add it into the list
            arb_size_list.append(arb_size)
            fn = "arbitor_" + str(arb_size) + "_masters.v"
            d = self.project_tags["BASE_DIR"] + "/rtl/bus/arbitors"
           
            self.filegen.buf = arbitor.generate_arbitor_buffer(arb_size)
            if debug: print "arbitor buffer: " + self.filegen.buf
            self.filegen.write_file(d, fn)
        return len(arb_size_list)
