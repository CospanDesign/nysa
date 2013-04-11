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

class PluginDocument():
  config_dict = {}
  output = None
  name = ""

  def __init__(self, name, output=None, dbg=False):
    self.dbg = dbg
    self.name = name
    self.config_dict = {}
    if output is None:
      self.output = main_status.Dummy(dbg)
      if self.dbg:
        self.output.SetLevel(StatusLevel.VERBOSE)
      else:
        self.output.SetLevel(StatusLevel.INFO)
    else:
      self.output = output

  def get_name(self):
    return self.name

  def set_config_dict(self, cd):
    config_dict = cd

  def get_config_dict(self):
    return config_dict

  def set_output(self, output):
    self.output = output

  def setup(self):
    self.output.Error (self, "Function not found")

  def save(self, file_path):
    self.output.Debug(self, "Saving File")

  def load(self, file_path):
    self.output.Debug(self, "Load File")


