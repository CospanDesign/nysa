#Distributed under the MIT licesnse.
#Copyright (c) 2011 Cospan Design (dave.mccoy@cospandesign.com)

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

"""Main interface for the ibuilder_lib package.

The command line interface will call this module in order to
create project configuration files and generate the entire project
"""

__author__ = 'dave.mccoy@cospandesign.com (Dave McCoy)'

"""Changes:
  06/07/2012
    -Added Documentation and licsense
"""

import os
import sys
import shutil
import json
import glob
import utils
import project_generator


#XXX: should be moved to the utils.py 'create_project_config_file' uses this
def get_interface_list (bus="wishbone"):
  """Return a list of interfaces associates with bus
  
  Args:
    bus: a string declaring the bus type, this can be
      \"wishbone\" or \"axie\"

  Returns:
    A list of interfaces that are supported by this board

  Raises:
    Nothing
  """
  interface_list = []
  return interface_list

def create_project_config_file(filename, bus = "wishbone", interface="uart_io_handler.v", base_dir = "~"):
  """Generate a configuration file for a project
  
  Given a filename, bus type, interface and base directory of the outputted
  project creates a json configuration file that can be used by 
  generate_project to create an FPGA image
  
  Args:
    filename: the name of the file that will be created
      example: \"config_file.json\"
    bus: a string declaring the bus type, this can be
      \"wishbone\" or \"axie\"
    interface: a string specifying the host interface module name
      example: \"uart_io_handler.v\"
    base_dir: the base directory of the output project
      example: \"~/project\"

  Returns:
    Nothing

  Raises:
    IOError: An error in file generation has occured
  """
  return 

def get_output_dir(filename, dbg = False):
  """Returns the output directory of a given configuration file"""
  filename = utils.resolve_path(filename)
  #let the user deal with Errors
  if dbg: print "filename: %s" % filename
  f = open(filename)
  config_dict = json.loads(f.read())
  f.close()
  return utils.resolve_path(config_dict["BASE_DIR"])



def generate_project(filename, dbg=False):
  """Generate a FPGA project
  
  The type of phroject is specific to the vendor called. For example, if the 
  configuration file specified that the vendor is Xilinx then the generated 
  project would be a PlanAhead project

  Args:
    filename: Name of the configuration file to be read

  Returns:
    A result of success or fail
      0 = Success
      -1 = Fail

  Raises:
    IOError: An error in project generation has occured
  """
  pg = project_generator.ProjectGenerator()
  result = pg.generate_project(filename, debug = dbg)
  return result
