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

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir))

from nysa.gui.main import main_status
from nysa.gui.main.main_status import StatusLevel

class Plugin():

  name = ""
  description = ""
  path  = ""
  dbg = False
  output=None

  def __init__(self, output=None, dbg=False):
    self.dbg = dbg
    if output is None:
      self.output = main_status.Dummy(dbg)
      if self.dbg:
        self.output.SetLevel(StatusLevel.VERBOSE)
      else:
        self.output.SetLevel(StatusLevel.INFO)
    else:
      self.output = output

  def set_output(self, output):
    self.output = output

  def setup(self):
    self.output.Error (self, "Function not found")

  def load_main_view(self):
    self.output.Error (self, "Function not found")

  def get_project_dictionary(self):
    self.output.Debug (self, "Getting project dictionary")

  def read_config_file(self, config_file_name="config.json"):
    #note: config_file_name is set to 'config.json' by default but this can be changed
    self.output.Debug (self, str("Reading configuration file: %s" % config_file_name))
    xbuf = ""
    full_path = ""
    full_path = os.path.join(self.path , config_file_name)
    self.output.Debug(self, ("full path %s" % full_path))
    config_dict = {}
    try:
      filein = open(full_path)
      self.output.Debug (self, "Opened the config file")
      #xbuf = filein.read()
      config_dict = json.load(filein)
    except IOError as err:
      self.output.Error (self, str("File Not Found! %s " % str(err)))

    self.name = config_dict["name"]
    self.description = config_dict["description"]
    return config_dict

