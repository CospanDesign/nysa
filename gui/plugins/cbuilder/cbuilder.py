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

import os
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))

from .. import plugin
import cbuilder_main_view as cmv
from nysa.gui.main import main_status
from nysa.gui.main.main_status import StatusLevel


class CBuilder (plugin.Plugin):
  name  = ""
  description = ""
  dbg = False

  def __init__(self, dbg=False):
    self.dbg = dbg
    plugin.Plugin.__init__(self, dbg = dbg)
    self.output.Debug (self, "cbuilder started")

  def setup_main_view(self, panel):
    self.output.Debug (self, "Setup main view")
    cbmv = cmv.CbuilderMainView()
    cbmv.setup_view(panel)

  def read_config_file(self, config_file_name="config.json"):
    return plugin.Plugin.read_config_file(self, config_file_name = config_file_name)

  def new_project(self, obj = None):
    self.output.Info(self, "In new project function")
