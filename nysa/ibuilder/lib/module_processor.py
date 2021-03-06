# Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)
#
# This file is part of Nysa.
#
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

# -*- coding: utf-8 -*-

"""Module Factory

Generates verilog modules. The generation of a verilog module may by simply
copying the module or generating the module with a script or a combination
of the two
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

"""Changes:
06/11/2012
    -Added Documentation and licsense
    -Moved two functions from sapfile to utils
      is_module_in_file
      find_module_filename
09/18/2013
    -Changed license to GPL V3
"""


import os
import glob
import sys
import importlib

from inspect import isclass
from ibuilder_error import ModuleNotFound
from ibuilder_error import ModuleFactoryError
import utils

sys.path.append(os.path.join( os.path.dirname(__file__),
                              "gen_scripts"))

sys.path.append(os.path.join( os.path.dirname(__file__),
                              os.pardir,
                              os.pardir,
                              "cbuilder",
                              "scripts"))

from gen_scripts import gen



class ModuleProcessor:
  """Generates a module

  Based on the script template the modules may be created with a gen script
  or simply copying a file
  """

  def __init__ (self, user_paths = []):
#    print "SAPLIB_BASE: " + os.environ["SAPLIB_BASE"]
#    print "Path: " + str(sys.path)
    self.user_paths = list(set(user_paths))
    self.gen_module = None
    self.gen = None
    self.buf = ""
    self.tags = {}
    self.verilog_file_list = []
    self.verilog_dependency_list = []
    return

  def write_file(self, location = "", filename=""):
    """write_file

    Search through the specified location, if the location doesn't exist then
    create the location.
    then write out the specified file

    Args:
      location: the location where the file is to be written
      filename: the name of the output file to write

    Returns:
      Nothing

    Raises:
      IOError
    """
    home = False
    location = utils.resolve_path(location)
    if not os.path.exists(location):
       utils.create_dir(location)
    fname = os.path.join(location, filename)
    fileout = open(fname, "w")
    fileout.write(self.buf)
    fileout.close()
    return

  def apply_tags(self):
    """apply_tags

    Substitutes that tags with the data specific to this project

    Args:
      None

    Return:
      Nothing

    Raises:
      KeyError
    """
    #search through the buf for any tags that match something within
    #our tag map
    try:
      self.buf = self.buf.format(self.tags)
    except KeyError as err:
      if ('$' in err):
        raise KeyError(str(err))
    except ValueError as err:
      print "Value Error with the Buffer (shown below): %s" % str(err)
      print "Tags:"
      for t in self.tags:
        print "\t%s: %s" % (t, str(self.tags[t]))
      print "Buffer: %s" % self.buf
    return

  def set_tags(self, tags={}):
    """set_tags

    set the tags for this module

    Args:
      tags: project specific tags

    Return:
      Nothing

    Raises:
      Nothing
    """
    self.tags = tags
    return

  def process_file(self, filename, file_dict, directory="", debug=False):
    """process_file

    read in a file, modify it (if necessary), then write it to the location
    specified by the directory variable

    Args:
      filename: the name of the file to process
      file_dict: dictionary associated with this file
      directory: output directory

    Return:

    Raises:
      ModuleFactoryError
      IOError

    """
    verbose = False
    debug = False
    if (filename.endswith(".v")):
        self.verilog_file_list.append(filename)

    if debug:
        print "in process file"
        print "\t%s" % filename
    #maybe load a tags??

    #using the location value in the file_dict find the file and
    #pull it into a buf

    self.buf = ""
    file_location = ""
    paths = self.user_paths


    #There are two types of files
    #ones that are copied over from a location
    #ones that are generated by scripts

    #The file is specified by a location and basically needs to be copied over
    if file_dict.has_key("location"):
        #print "Location: %s" % file_dict["location"]
        #file_location = os.path.join( utils.nysa_base,
        loc = file_dict["location"].split("/")
        #print "Loc list: %s" % str(loc)
        if loc[0] == "${NYSA}":
            loc[0]  = utils.nysa_base


        #print "Loc list: %s" % str(loc)

        file_location = "/"
        for d in loc:
            file_location = os.path.join(file_location, d)

        if (debug):
            print ("getting file: " + filename + " from location: " + file_location)

        found_file = False
        try:
            filein = open(os.path.join(utils.resolve_path(file_location), filename))
            self.buf = filein.read()
            filein.close()
            found_file = True
        except IOError as err:
            pass

        if not found_file:
            if debug:
                print "searching for file...",
            try:
                absfilename = utils.find_rtl_file_location(filename, self.user_paths)
                filepath = os.path.dirname(os.path.dirname(absfilename))
                paths.insert(0, filepath)
                paths = list(set(paths))

                filein = open(absfilename)
                self.buf = filein.read()
                filein.close()

            except:
                if debug:
                    print "Failed to find file"
                raise ModuleFactoryError("File %s not found searched %s and in the HDL dir (%s)" %  (filename, \
                                          file_location, \
                                          utils.nysa_base + os.path.sep + "cbuilder" + os.path.sep + "verilog"))


        if verbose:
          print "found file!"
          print "file content: " + self.buf

    #File is generated by a script
    elif (not file_dict.has_key("gen_script")):
      raise ModuleFactoryError( "File %s does not declare a location or a \
                                  script! Check the template file" % filename)

    if verbose:
      print "Project name: " + self.tags["PROJECT_NAME"]

    #if the generation flag is set in the dictionary
    if "gen_script" in file_dict:
      if debug:
        print "found the generation script"
        print "run generation script: " + file_dict["gen_script"]
      #open up the new gen module
      ms = sys.modules.keys()
      gs = ""
      for m in ms:
          if m.endswith("gen_scripts"):
              gs = m
      #print "gs: %s" % gs


      cl = __import__("%s.gen" % gs, fromlist=[gs])
      #cl = importlib.import_module("gen_scripts", "gen")
      #if debug:
      #  print "cl: " + str(cl)
      Gen = getattr(gen, "Gen")
      if debug:
        print "Gen: " + str(Gen)
      self.gen_module = __import__("%s.%s" % (gs, file_dict["gen_script"]), fromlist=[gs])
      gen_success_flag = False

      #find the script and dynamically add it
      for name in dir(self.gen_module):
        obj = getattr(self.gen_module, name)
  #      print "object type: " + str(obj)
#XXX: debug section start
        if verbose:
          print "name: " + name
        if isclass(obj):
          if verbose:
            print "\tobject type: " + str(obj)
            print "\tis class"
          if issubclass(obj, cl.Gen):
            if verbose:
              print "\t\tis subclass"
#XXX: debug section end
        if isclass(obj) and issubclass(obj, cl.Gen) and obj is not cl.Gen:
          self.gen = obj()
          if verbose:
            print "obj = " + str(self.gen)

          self.buf = self.gen.gen_script(tags = self.tags, buf = self.buf, user_paths = self.user_paths)
          gen_success_flag = True

      if not gen_success_flag:
        raise ModuleFactoryError("Failed to execute the generation script %s" %
                                  file_dict["gen_script"])
    else:
      #no script to execute, just tags
      self.apply_tags()

    if verbose:
      print self.buf
    if (len(self.buf) > 0):
      result = self.write_file(directory, filename)

    if self.has_dependencies(filename):
      deps = self.get_list_of_dependencies(filename)
      for d in deps:
        try:
          f = utils.find_module_filename(d, self.user_paths)
          if (len(f) == 0):
            print "Error: couldn't find dependency filename"
            continue
          if (f not in self.verilog_dependency_list and
            f not in self.verilog_file_list):
            if debug:
              print "found dependency: " + f
            self.verilog_dependency_list.append(f)
        except ModuleNotFound as err:
          continue

  def resolve_dependencies(self, filename, debug = True):
    """resolve_dependencies

    given a filename determine if there are any modules it depends on,
    recursively search for any files found in order to extrapolate all
    dependencies

    Args:
      filename: The filename to resolve dependencies for

    Return:
      Nothing

    Raises:
      ModuleFactoryError
    """

    result = True
    ldebug = debug
    if debug:
      print "in resolve dependencies"
    local_file_list = []
    if debug:
      print "working on filename: " + filename
    if (self.has_dependencies(filename, debug = ldebug)):
      if debug:
        print "found dependencies!"
      deps = self.get_list_of_dependencies(filename, debug = ldebug)
      for d in deps:
        try:
          dep_filename = utils.find_module_filename(d, self.user_paths, debug = ldebug)
        except ModuleNotFound as ex:
          print "Dependency Warning: %s" % (str(ex))
          print "Module Name: %s" % (d)
          print "This warning may be due to:"
          print "\tIncluding a simulation only module"
          print "\tIncluding a vendor specific module"
          print "\tA module that was not found"
          continue

        if debug:
          print "found the filename: " + dep_filename
        #check this file out for dependecies, then append that on to the local list
        self.resolve_dependencies(dep_filename, debug = ldebug)
        if debug:
          print "found all sub dependencies for: " + dep_filename
        local_file_list.append(dep_filename)

    #go through the local file list and add anything found to the list of dependencies or verilog files
    for f in local_file_list:
      if (f not in self.verilog_dependency_list) and (f not in self.verilog_file_list):

        if debug:
          print "found dependency: " + f
        self.verilog_dependency_list.append(f)

    return

  def has_dependencies(self, filename, debug = False):
    """has_dependencies

    returns true if the file specified has dependencies

    Args:
      filename: search for dependencies with this filename

    Return:
      True: The file has dependencies.
      False: The file doesn't have dependencies

    Raises:
      IOError
    """
    if debug:
      print "input file: " + filename
    #filename needs to be a verilog file
    if (filename.partition(".")[2] != "v"):
      if debug:
        print "File is not a recognized verilog source"
      return False

    fbuf = ""

    #the name is a verilog file, try and open is
    try:
      filein = open(filename)
      fbuf = filein.read()
      filein.close()
    except IOError as err:
      if debug:
        print "the file is not a full path, searching RTL... ",
      #didn't find with full path, search for it
      try:
        #print "self.user_paths: %s" % (self.user_paths)
        filepath = utils.find_rtl_file_location(filename, self.user_paths)

        filein = open(filepath)
        fbuf = filein.read()
        filein.close()
      except ModuleNotFound as err:
        fbuf = ""
      except IOError as err_int:
        if debug:
          print "couldn't find file in the RTL directory"
        ModuleFactoryError("Couldn't find file %s in the RTL directory" % filename)


    #we have an open file!
    if debug:
      print "found file!"

    #strip out everything we can't use
    fbuf = utils.remove_comments(fbuf)

    #modules have lines that start with a '.'
    str_list = fbuf.splitlines()

    for item in str_list:
      item = item.strip()
      if (item.startswith(".")):
        if debug:
          print "found a module!"
        return True
    return False

  def get_list_of_dependencies(self, filename, debug=False):
    """get_list_of_dependencies

    return a list of the files that this file depends on

    Args:
      filename: the name of the file to analyze

    Return:
      A list of files that specify the dependenies

    Raises:
      IOError
    """
    deps = []
    if debug:
      print "input file: " + filename
    #filename needs to be a verilog file
    if (filename.partition(".")[2] != "v"):
      if debug:
        print "File is not a recognized verilog source"
      return False

    fbuf = ""
    #the name is a verilog file, try and open is
    try:
      filein = open(filename)
      fbuf = filein.read()
      filein.close()
    except IOError as err:
      #if debug:
      #  print "the file is not a full path... searching RTL"
      #didn't find with full path, search for it
      try:
        filepath = utils.find_rtl_file_location(filename, self.user_paths)

        filein = open(filepath)
        fbuf = filein.read()
        filein.close()
      except IOError as err_int:
        ModuleFactoryError("Couldn't find file %s in the RTL directory" % filename)


    #we have an open file!
    if debug:
      print "found file!"

    #strip out everything we can't use
    fbuf = utils.remove_comments(fbuf)

    include_fbuf = fbuf
    #search for `include
    while (not len(include_fbuf.partition("`include")[2]) == 0):
      ifile_name = include_fbuf.partition("`include")[2]
      ifile_name = ifile_name.splitlines()[0]
      ifile_name = ifile_name.strip()
      ifile_name = ifile_name.strip("\"")
      if debug:
        print "found an include " + ifile_name + " ",
      if (ifile_name not in self.verilog_dependency_list) and (ifile_name not in self.verilog_file_list):
        self.verilog_dependency_list.append(ifile_name)
        if debug:
          print "adding " + ifile_name + " to the dependency list"
      else:
        if debug:
          print "... already in have it"
      include_fbuf = include_fbuf.partition("`include")[2]

    #remove the ports list and the module name
    fbuf = fbuf.partition(")")[2]

    #modules have lines that start with a '.'
    str_list = fbuf.splitlines()

    module_token = ""
    done = False
    while (not done):
      for i in range (0, len(str_list)):
        line = str_list[i]
        #remove white spaces
        line = line.strip()
        if (line.startswith(".") and line.endswith(",")):
          #if debug:
          #  print "found a possible module... with token: " + line
          module_token = line
          break
        #check if we reached the last line
        if (i >= len(str_list) - 1):
          done = True

      if (not done):
        #found a possible module
        #partitoin the fbuf
        #if debug:
        #  print "module token " + module_token
        module_string = fbuf.partition(module_token)[0]
        fbuf = fbuf.partition(module_token)[2]
        fbuf = fbuf.partition(";")[2]
        str_list = fbuf.splitlines()

        #get rid of everything before the possible module
        while (len(module_string.partition(";")[2]) > 0):
          module_string = module_string.partition(";")[2]

        module_string = module_string.partition("(")[0]
        module_string = module_string.strip("#")
        module_string = module_string.strip()

        m_name = module_string.partition(" ")[0]
        if debug:
          print "module name: " + m_name

        if (not deps.__contains__(m_name)):
          if debug:
            print "adding it to the deps list"
          deps.append(module_string.partition(" ")[0])


        #mlist = module_string.splitlines()
        #work backwords
        #look for the last line that has a '('
        #for i in range (0, len(mlist)):
        #  mstr = mlist[i]
        #  print "item: " + mlist[i]
        #  #mstr = mlist[len(mlist) - 1 - i]
        #  #mstr = mstr.strip()
        #  if (mstr.__contains__(" ")):
        #    if debug:
        #      print "found: " + mstr.partition(" ")[0]
        #    deps.append(mstr.partition(" ")[0])
        #    break


    return deps

