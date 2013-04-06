#Distributed under the MIT licesnse.
#Copyright (c) 2013 Dave McCoy (dave.mccoy@cospandesign.com)

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

import json
import sys
import os
import copy

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir))

from nysa.gui.main import main_status
from nysa.gui.main.main_status import StatusLevel

class PluginProject():

  name = ""
  description = ""
  path  = ""
  dbg = False
  output=None
  config_dict = {}
  class_config_dict = {}
  new_project_wiz_en = False


  def __init__(self, output=None, name = None, dbg=False):
    self.dbg = dbg
    if output is None:
      self.output = main_status.Dummy(dbg)
      if self.dbg:
        self.output.SetLevel(StatusLevel.VERBOSE)
      else:
        self.output.SetLevel(StatusLevel.INFO)
    else:
      self.output = output
    self.name = name
    #create a deep copy so we don't mess up the original configuration file
    self.config_dict = copy.deepcopy(self.class_config_dict)

    #go through the config dictionary and map any functions to where they are supposed to go
    self.output.Info(self, str("Path: %s" % self.path))
    self._map_functions(self.config_dict)

  def set_output(self, output):
    self.output = output

  def set_name(self, name):
    self.name = name

  def load_project(self):
    pass

  def close_project(self):
    pass

  def save_project(self):
    pass

  def load_project(self):
    pass

  def new_project(self):
    self.output.Info(self, "Setting up a new project")

  def is_new_project_wizard(self):
    return False

  def get_new_project_wizard(self):
    return self.config_dict["new_project_wizard"]

  def _map_functions(self, config_level):

    if type(config_level) == list:
      for x in xrange (len(config_level)):
        if type(config_level[x]) == dict:
          self._map_functions(config_level[x])
      return

    elif type(config_level) == dict:
      if len(config_level.keys()) == 0:
        return


      for key in config_level.keys():
        if "list" == key:
          if type(config_level[key]) == str or type(config_level[key]) == unicode:

            func_name = config_level[key]

            #self.output.Info(self, "Directory of class: %s" % str(dir(self)))
            for attr in dir(self):
              #self.output.Info(self, str("Check if %s == %s" % (func_name, str(attr))))
              if func_name == str(attr):
                self.output.Info(self, str("Found: %s" % func_name))
                temp = config_level[key]
                config_level[key] = getattr(self, attr)
                self.output.Debug(self, str("Rempaing %s to %s" % (temp, config_level[key])))

        elif type(config_level[key]) == list:
          self._map_functions(config_level[key])

        elif type(config_level[key]) == dict:
          self._map_functions(config_level[key])
    return





