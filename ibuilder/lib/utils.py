# Distributed under the MIT licesnse.
# Copyright (c) 2011 Dave McCoy (dave.mccoy@cospandesign.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
"""


__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

import os
import sys
import string
import glob
import json

import preprocessor
import arbitor

from ibuilder_error import ModuleNotFound
from ibuilder_error import NysaEnvironmentError

nysa_base = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

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
  if debug:
    print "Directory to create: ", dirname

  if  (not os.path.exists(dirname)):
    if debug:
      print ("Directory doesn't exist attempting to create...")
#XXX: this error should be raised for the user
    try:
      os.makedirs(dirname)
    except os.error:
      if debug:
        print "Error: failed to create the directory"
  else:
    if debug:
      print ("Found the directory")
  return True

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
  if (filename.startswith("~")):
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

def find_rtl_file_location(filename="", user_cbuilder_paths = [], debug=False):
  """Finds a RTL file in the cbuilder rtl directory.

  Args:
    filename: the name of a verilog file to search for
    user_cbuilder_paths: list of paths to search for cbuilder projects

  Returns:
    If found, The absolute path of the verilog module file,
    Otherwise an empty string

  Raises:
    Nothing
  """
   #Get the base directory of Nysa and look in the cbuilder director
  base_location = nysa_base
  base_location = os.path.join(base_location, "cbuilder", "verilog")
#  print "rtl dir: " + base_location
  for root, dirs, names in os.walk(base_location):
    if filename in names:
#      print "Filename: " + filename
      return os.path.join(root, filename)

  if debug: print "Looking in custom path: %s" % user_cbuilder_paths

  for path in user_cbuilder_paths:
    for root, dirs, names in os.walk(path):
      if filename in names:
        return os.path.join(root, filename)

  raise ModuleNotFound("File: %s not found, looked in %s and the default location %s" % (filename, str(user_cbuilder_paths), base_location))
#XXX: This should probably return none, and not an empty string upon failure
#XXX:   perhaps even raise an error

def get_module_tags(filename="", bus="", keywords = [], debug=False):
  """Gets the tags for the module within the specified filename

  Given a module within a filename search through the module and
  find:
    metadata
      \"DRT_ID\"
      \"DRT_FLAGS\"
    ports: Inputs/Outputs of this module
    module: Name of the module
    parameters: Configuration parameters within the module
    arbitor_masters: Any arbitor masters within the module

  Args:
    filename: Name of the module to interrogate
    bus: A string declaring the bus type, this can be
      \"wishbone\" or \"axie\"
    keywords:
      Besides the standard metadata any additional values to search for

  Returns:
    A dictionary of module tags

  Raises
    Nothing
  """
  tags = {}
  tags["keywords"] = {}
  tags["ports"] = {}
  tags["module"] = ""
  tags["parameters"] = {}
  tags["arbitor_masters"] = []
  raw_buf = ""

  #need a more robust way of openning the slave

#  keywords = [
#    "DRT_ID",
#    "DRT_FLAGS",
#  ]

  ports = [
    "input",
    "output",
    "inout"
  ]


  #XXX only working with verilog at this time, need to extend to VHDL
  #print "filename: %s" % filename

  with open(filename) as slave_file:
    buf = slave_file.read()
    raw_buf = buf


  #find all the metadata
  for key in keywords:
    index = buf.find (key)
    if (index == -1):
      if debug:
        print "didn't find substring for " + key
      continue
    if debug:
      print "found substring for " + key

    substring = buf.__getslice__(index, len(buf)).splitlines()[0]
    if debug:
      print "substring: " + substring


    if debug:
      print "found " + key + " substring: " + substring

    substring = substring.strip()
    substring = substring.strip("//")
    substring = substring.strip("/*")
    tags["keywords"][key] = substring.partition(":")[2]



  #remove all the comments from the code
  buf = remove_comments(buf)
  #print "no comments: \n\n" + buf

  for substring in buf.splitlines():
    if (len(substring.partition("module")[1]) == 0):
      continue
    module_string = substring.partition("module")[2]
    module_string = module_string.strip(" ")
    module_string = module_string.strip("(")
    module_string = module_string.strip("#")
    index = module_string.find(" ")

    if (index != -1):
      tags["module"] = module_string.__getslice__(0, index)
    else:
      tags["module"] = module_string

    if debug:
      print "module name: " + module_string
      print tags["module"]

    break

  #find all the ports
  #find the index of all the processing block
  substrings = buf.splitlines()

  input_count = buf.count("input")
  output_count = buf.count("output")
  inout_count = buf.count("inout")

  if debug:
    print "filename: " + filename

  filestring = ""
  try:
    f = open(filename)
    filestring = f.read()
    f.close()
#XXX: This should probably allow the calling function to handle a failure
  except:
    print "Failed to open test filename"
    return

  ldebug = debug
  define_dict = preprocessor.generate_define_table(filestring, ldebug)

  #find all the IO's
  for io in ports:
    tags["ports"][io] = {}
    substrings = buf.splitlines()
    for substring in substrings:
#      if debug:
#        print "working on substring: " + substring
      substring = substring.strip()
      #if line doesn't start with an input/output or inout
      if (not substring.startswith(io)):
        continue
      #if the line does start with input/output or inout but is used in a name then bail
      if (not substring.partition(io)[2][0].isspace()):
        continue
      #one style will declare the port names after the ports list
      if (substring.endswith(";")):
        substring = substring.rstrip(";")
      #the other stile will include the entire port definition within the port declaration
      if (substring.endswith(",")):
        substring = substring.rstrip(",")
      if debug:
        print "substring: " + substring
      substring = substring.partition(io)[2]
      if (len(substring.partition("reg")[1]) != 0):
        substring = substring.partition("reg")[2]
      substring = substring.strip()
      max_val = -1
      min_val = -1
      if (len(substring.partition("]")[2]) != 0):
        #we have a range to work with?
        length_string = substring.partition("]")[0] + "]"
        substring = substring.partition("]")[2]
        substring = substring.strip()
        length_string = length_string.strip()
        if debug:
          print "length string: " + length_string

        ldebug = debug

        length_string = preprocessor.resolve_defines(length_string, define_dict, debug=ldebug)
        length_string = preprocessor.evaluate_range(length_string)
        length_string = length_string.partition("]")[0]
        length_string = length_string.strip("[")
        if debug:
          print "length string: " + length_string
        max_val = string.atoi(length_string.partition(":")[0])
        min_val = string.atoi(length_string.partition(":")[2])

      tags["ports"][io][substring] = {}

      if (max_val != -1):
        tags["ports"][io][substring]["max_val"] = max_val
        tags["ports"][io][substring]["min_val"] = min_val
        tags["ports"][io][substring]["size"] = (max_val + 1) - min_val
      else:
        tags["ports"][io][substring]["size"] = 1

      #print io + ": " + substring


  #find all the USER_PARAMETER declarations
  user_parameters = []
  substrings = raw_buf.splitlines()
  for substring in substrings:
    substring = substring.strip()
    if "USER_PARAMETER" in substring:
      name = substring.partition(":")[2].strip()
      user_parameters.append(name)


  #find all the parameters
  substrings = buf.splitlines()
  for substring in substrings:
    substring = substring.strip()
    if ("parameter" in substring):
      if debug:
        print "found parameter!"
      substring = substring.partition("parameter")[2].strip()
      parameter_name = substring.partition("=")[0].strip()
      parameter_value = substring.partition("=")[2].strip()
      parameter_value = parameter_value.partition(";")[0].strip()
      if debug:
        print "parameter name: " + parameter_name
        print "parameter value: " + parameter_value
      if parameter_name in user_parameters:
        tags["parameters"][parameter_name] = parameter_value


  tags["arbitor_masters"] = arbitor.get_number_of_arbitor_hosts(tags)


  if debug:
    print "input count: " + str(input_count)
    print "output count: " + str(output_count)
    print "inout count: " + str(inout_count)
    print "\n"

  if debug:
    print "module name: " + tags["module"]
    for key in tags["keywords"].keys():
      print "key: " + key + ":" + tags["keywords"][key]
    for io in ports:
      for item in tags["ports"][io].keys():
        print io + ": " + item
        for key in tags["ports"][io][item].keys():
          value = tags["ports"][io][item][key]
          if (isinstance( value, int)):
            value = str(value)
          print "\t" + key + ":" + value

  return tags


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
  #print "Nysa Base: %s" % base
  #base = os.path.abspath(os.path.join(base, os.pardir, os.pardir))

  """
  try:
    f = open(path)
    s = f.read()
    nysa_config = json.loads(s)
    f.close()
    #print "Opened up the configuration file"

  except IOError:
    raise NysaEnvironmentError("Error user has not set up configuration file,\
    run 'init_settings.py' in nysa base directory")

  #Get the base directory of Nysa and look in the cbuilder director
  return nysa_config["dir"]
  """
  return nysa_base

def get_board_names (debug = False):
  """Returns a list of all the board names"""
  base_location = nysa_base
  base_location = os.path.join(base_location, "ibuilder", "boards")
  boards = []

  for root, dirs, names in os.walk(base_location):
    if debug:
      print "Dirs: " + str(dirs)

    for bn in dirs:
      boards.append(bn)

  return boards

def get_constraint_filenames (board_name, debug = False):
  """Returns a list of ucf files for the specified board name"""
  board_dir = os.path.join(nysa_base, "ibuilder", "boards", board_name)
  if debug: print "Board dir: %s" % board_dir
  cfiles = []
  for root, dirs, names in os.walk(board_dir):
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

def get_board_config (board_name, debug = False):
  """Returns a dictionary of board specific information

  Args:
    board_name: the name of the board to get the information from
      Example: \"sycamore1\"

  Returns:
    A dictionary of the board configuration data

  Raises:
    Nothing
  """
  board_dir = os.path.join(nysa_base, "ibuilder", "boards")
  if debug: print "Board dir: %s" % board_dir

  filename = ""
  buf = ""
  board_dict = {}

  if debug: print "Looking for: " + board_name

  for root, dirs, names in os.walk(board_dir):
    if debug:
      print "Dirs: " + str(dirs)

    if board_name in dirs:
      if debug:
        print "Found the directory"

      filename = os.path.join(root, board_name)
      filename += "/config.json"
      if debug:
        print "filename: %s" % filename
      break

  if len(filename) == 0:
    if debug:
      print "didn't find board config file"
    return {}


  #open up the config file
  try:
    file_in = open(filename)
    buf = file_in.read()
    board_dict = json.loads(buf)
    file_in.close()
#XXX: This should probably raise an error to the calling function
  except:
    #fail
    if debug:
      print "failed to open file: " + filename
    return ""

  if debug:
    print "Opened up the board config file for %s" % (board_name)

#for debug
  return board_dict

def get_net_names(constraint_filename, debug = False):
  """Gets a list of net in a given constraint file

  Args:
    constrint_filename: name of a constraint file with an absolute path

  Returns:
    A list of constraint for the module
    NOTE: This file fails quietly and shouldn't this needs to be fixed!

  Raises:
    Nothing
  """

  board_dir = os.path.join(nysa_base, "ibuilder", "boards")
  filename = ""
  buf = ""
  nets = []


  if debug:
    print "Looking for: " + constraint_filename
  for root, dirs, names in os.walk(board_dir):
    if debug:
      print "name: " + str(names)

    if constraint_filename in names:
      if debug:
        print "found the file!"
      filename =  os.path.join(root, constraint_filename)
      break

  if (len(filename) == 0):
    if debug:
      print "didn't find constraint file"
    return ""

  #open up the ucf file
  try:
    file_in = open(filename)
    buf = file_in.read()
    file_in.close()
  except:
    #fail
#XXX: This should probably allow the calling function to handle a failure
    if debug:
      print "failed to open file: " + filename
    return ""

  if debug:
    print "Opened up the UCF file"

  lines = buf.splitlines()
  #first search for the TIMESPEC keyword
  for line in lines:
    line = line.lower()
    #get rid of comments
    if ("#" in line):
      line = line.partition("#")[0]

    if "net" not in line:
      continue

    #split separate all space deliminated tokens
    line = line.partition("net")[2].strip()
    token = line.split()[0]
    token = token.strip("\"")

    token = token.replace('<', '[')
    token = token.replace('>', ']')
#    if debug:
#      print "possible net name: " + token

    if token not in nets:
      nets.append(token)

  return nets

def read_clock_rate(constraint_filename, debug = False):
  """Returns a string of the clock rate

  Searches through the specified constraint file to determine if there
  is a specified clock. If no clock is specified then return 50MHz = 50000000

  Args:
    constraint_filename: the name of the constraint file to search through

  Returns:
    A string representation of the clock rate
    NOTE: on error this fails quietly this should probably be different

  Raises:
    Nothing
  """
  board_dir = os.path.join(nysa_base, "ibuilder", "boards")
  filename = ""
  buf = ""
  clock_rate = ""
#  print "rtl dir: " + board_dir
  if debug:
    print "Looking for: " + constraint_filename
  for root, dirs, names in os.walk(board_dir):
    if debug:
      print "name: " + str(names)

    if constraint_filename in names:
      if debug:
        print "found the file!"
      filename =  os.path.join(root, constraint_filename)
      break

  if (len(filename) == 0):
    if debug:
      print "didn't find constraing file"
    return ""

  #open up the ucf file
  try:
    file_in = open(filename)
    buf = file_in.read()
    file_in.close()
  except:
#XXX: This should probably allow the calling function to handle a failure
    #fail
    if debug:
      print "failed to open file: " + filename
    return ""

  if debug:
    print "Opened up the UCF file"

  lines = buf.splitlines()
  #first search for the TIMESPEC keyword
  for line in lines:
    line = line.lower()
    #get rid of comments
    if ("#" in line):
      line = line.partition("#")[0]

    #is this the timespec for the "clk" clock?
    if ("timespec" in line) and ("ts_clk" in line):
      if debug:
        print "found timespec"
      #this is the "clk" clock, now read the clock value
      if debug:
        print "found TIMESPEC"
      line = line.partition("period")[2].strip()
      if debug:
        print "line: " + line
      line = line.partition("clk")[2].strip()
      line = line.strip("\"");
      line = line.strip();
      line = line.strip(";")
      if debug:
        print "line: " + line

      #now there is a time value and a multiplier
      clock_lines = line.split(" ")
      if debug:
        for line in clock_lines:
          print "line: " + line

      if (clock_lines[1] == "mhz"):
        clock_rate = clock_lines[0] + "000000"
      if (clock_lines[1] == "khz"):
        clock_rate = clock_lines[0] + "000"


  #if that didn't work search for the PERIOD keyword, this is an older version
  if (len(clock_rate) == 0):
    if debug:
      print "didn't find TIMESPEC, looking for period"
    #we need to check period
    for line in lines:
      #get rid of comments
      line = line.lower()
      if ("#" in line):
        line = line.partition("#")[0]
      if ("period" in line) and  ("clk" in line):
        if debug:
          print "found clock period"
        line = line.partition("period")[2]
        line = line.partition("=")[2].strip()
        if " " in line:
          line = line.partition(" ")[0].strip()
        if debug:
          print "line: " + line
        clock_rate = str(int(1/(string.atoi(line) * 1e-9)))
        break;

  if debug:
    print "Clock Rate: " + clock_rate
  return clock_rate


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

    if "DRT_ID" not in data:
      continue
    if "DRT_FLAGS" not in data:
      continue
    if "DRT_SIZE" not in data:
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






def get_slave_list(bus = "wishbone", user_cbuilder_paths = [], debug = False):
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
  directory = os.path.join(nysa_base, "cbuilder", "verilog", bus, "slave")

  file_list = _get_file_recursively(directory)

  slave_list = _get_slave_list(directory, debug=debug)

  for path in user_cbuilder_paths:
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
  cwd = os.getcwd()

  os.chdir(directory)
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
      while len(f.partition("/")[2]):
        f = f.partition("/")[2]

      if debug:
        print "Found a file with the name: " + f
      filename = f
      break

  os.chdir (cwd)
  if len(filename) == 0:
    raise ModuleNotFound("Searched in standard hdl/rtl location for file \
      containing the module %s" % module_name)
  return filename




def find_module_filename (module_name, user_cbuilder_paths = [], debug = False):
  cwd = os.getcwd()
  filename = ""
  if debug: print "nysa base: %s" % nysa_base
  base = os.path.join(nysa_base, "cbuilder", "verilog")
  if debug: print "Search directory: %s" % base
  try:
    return _find_module_filename(base, module_name, debug = debug)
  except ModuleNotFound, mnf:
    if debug: print "Did not find the file in nysa directory"
  finally:
    os.chdir(cwd)

  for path in user_cbuilder_paths:
    try:
      return _find_module_filename(base, module_name, debug = debug)
    except ModuleNotFound, mnf:
      pass
    finally:
      os.chdir(cwd)

  os.chdir(cwd)
  raise ModuleNotFound ("Module %s not found: Searched in Nysa directory: %s as well as the following directories %s" % (module_name, base , str(user_cbuilder_paths)))


def _get_file_recursively(directory):
  file_dir_list = glob.glob(directory + "/*")
  file_list = []
  for f in file_dir_list:
    if (os.path.isdir(f)):
      if   (f.split("/")[-1] != "sim"):
        file_list += _get_file_recursively(f)
    elif (os.path.isfile(f)):
      if f.endswith(".v"):
        file_list.append(f)

  return file_list
