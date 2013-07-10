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
  06/07/2012
    -Added Documentation and licsense
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import sys
import os
from os.path import exists
import shutil
from inspect import isclass
import json
import module_processor
import utils
import arbitor
from ibuilder_error import ModuleFactoryError

class ProjectGenerator:
  """Generates IBuilder Projects"""

  def __init__(self, user_paths = []):
    self.user_paths = user_paths
    self.filegen = module_processor.ModuleProcessor(user_paths = self.user_paths)
    self.project_tags = {}
    self.template_tags = {}
    return

  def read_config_string(self, json_string=""):
    """Reads in a configuration file string and creates a class dictionary

    Args:
      json_string: A JSON string containing the project configurtion data

    Return:
      Nothing

    Raises:
      TypeError
    """
    #this will throw a type error if there is a mistake in the JSON
    self.project_tags = json.loads(json_string)

  def read_config_file(self, filename="", debug=False):
    """Read in a configuration file name and create a class dictionary

    Args:
      filename: the filename of the configuration file to read in

    Return:
      Nothing

    Raises:
      TypeError
    """
    if debug: print "File to read: " + filename
    json_string = ""
#XXX: Should I allow file errors to propaget up to the user?
    #try:
    #open up the specified JSON project config file
    filein = open (filename)
    #copy it into a buffer
    json_string = filein.read()
    filein.close()

    #except IOError as err:
    #  raise IOError("Configuration file %s not found" % filename)

    #now we have a buffer call the read config string
    self.read_config_string(json_string)

  def read_template(self, template_filename="", debug=False):
    """Read the template file associatd with this bus

    Each type of bus (currently wishbone and axie) has their own
    template file, this function opens ups and parses out the template
    file into a dictionary. This is used by the project to populate
    the outputted project

    Args:
      template_filename: the name of the template file for the
        associated bus

    Return:
      Nothing

    Raises:
      TypeError
      IOError
    """

    self.template_tags = None

    if (debug):
      print "Debug enabled"

    if (self.template_tags is None and not template_filename.endswith(".json")):
      template_filename = template_filename + ".json"

    try:
      if (debug):
        print "attempting local"
      filein = open(template_filename, "r")
      json_string = filein.read()
      self.template_tags = json.loads(json_string)
      filein.close()
      return
    except IOError as err:
      pass

    filename = os.path.join(utils.get_nysa_base(), "ibuilder", "templates", template_filename)
    if (debug): print "Attempting default template location for %s" % template_filename
    f = open(filename, "r")
    json_string = f.read()
    self.template_tags = json.loads(json_string)
    f.close()

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
    #reading the project config data into the the project tags
#XXX: This should be changed to an exception begin raised and not a True False statement
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
    self.project_tags["CLOCK_RATE"] = utils.read_clock_rate(cfiles[0])

    self.read_template(self.project_tags["TEMPLATE"])

    #set all the tags within the filegen structure
    if debug:
      print "set all tags wihin filegen structure"
    self.filegen.set_tags(self.project_tags)

    #generate the project directories and files
    utils.create_dir(self.project_tags["BASE_DIR"])
    if debug:
      print "generated the first dir"

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

    if debug:
      print "generating project directories finished"

    if debug:
      print "generate the arbitors"

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
      if (len(constraint_path) == 0):
        print "Couldn't find constraint: " + constraint_fname + ", searched in current directory and " + sap_abs_base + " /hdl/" + self.project_tags["board"]
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
      file_dest = self.project_tags["BASE_DIR"] + "/dependencies"
      result = self.filegen.process_file(filename = d, file_dict = fdict, directory = file_dest)
      if debug:
        print d
    return True

  def get_constraint_path (self, constraint_fname, debug = False):
    """get_constraint_path

    given a constraint file name determine where that constraint it

    Args:
      constraint_fname: the name of the constraint file to search for

    Return:
      path of the constraint

    Raises:
      IOError
    """
    board_name  = self.project_tags["board"]
    
    if (exists(os.getcwd() + "/" + constraint_fname)):
      return os.getcwd() + "/" + constraint_fname

    #search through the board directory
    board_dir = os.path.join(utils.get_nysa_base(), "ibuilder", "boards", board_name, constraint_fname)
    if debug: print "Board Dir: %s" % board_dir
    if (exists(board_dir)):
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
    if (parent_dict[key].has_key("dir") and parent_dict[key]["dir"]):
      #print "found dir"
#      if (key == "arbitors" and ("ARBITORS" in self.project_tags.keys() ) and (len(self.project_tags["ARBITORS"].keys()) > 0)):
#        return True
      new_dir = os.path.join(parent_dir, key)
      if os.path.exists(new_dir) and parent_dir is not self.project_tags["BASE_DIR"]:
          #if we are not the base directory and the directory exists, remove it so we are clean
          #there is a check for the base directory because the user might put the project
          #in a pre-existing directory that would be obliterated
          shutil.rmtree(new_dir)
      utils.create_dir(parent_dir + os.path.sep + key)
      if (parent_dict[key].has_key("files")):
        for sub_key in parent_dict[key]["files"]:
          #print "sub item :" + sub_key
          self.recursive_structure_generator(
              parent_dict = parent_dict[key]["files"],
              key = sub_key,
              parent_dir = parent_dir + "/" + key)
    else:
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
#    arb_tags = arbitor.generate_arbitor_tags(self.project_tags, False)
#    self.project_tags["ARBITORS"] = arb_tags

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
      if debug:
        print "arbitor buffer: " + self.filegen.buf
      self.filegen.write_file(d, fn)

    return len(arb_size_list)
