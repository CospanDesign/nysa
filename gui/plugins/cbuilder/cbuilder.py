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


class CBuilder (plugin.Plugin):
  name  = ""
  description = ""

  def __init__(self):
    print "Hello from cbuilder"

  def setup_main_view(self, panel):
    print "Setup main view"
    cbmv = cmv.CbuilderMainView()
    cbmv.setup_view(panel)

  def read_config_file(self):
    #note: config_file_name is set to 'config.json' by default but this can be changed
    xbuf = ""
    full_path = ""
    #full_path = os.path.dirname(sys.modules[self.__module__])
    full_path = os.path.join(self.path , self.config_file_name)
    print "full path %s" % full_path
    config_dict = {}
    try:
      filein = open(full_path)
      print "Opened the file!"
      #xbuf = filein.read()
      config_dict = json.load(filein)
    except IOError as err:
      print "File Error: " + str(err)

    self.name = config_dict["name"]
    self.description = config_dict["description"]
    print "name: %s" % self.name
    print "description: %s" % self.description

