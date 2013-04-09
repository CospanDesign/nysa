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
import inspect
import plugin_document
import json

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))

from nysa.gui.main import main_status
from nysa.gui.main.main_status import StatusLevel


class DocumentPluginManager():
  output = None

  plugin_dict = None

  def __init__(self, output = None, dbg = False):
    if output is None:
      self.output = main_status.Dummy()
      if dbg:
        self.output.SetLevel(StatusLevel.VERBOSE)
      else:
        self.output.SetLevel(StatusLevel.INFO)
    else:
      self.output = output

    self.output.Debug(self, "Started")

    self.load_plugin_dict()
    for key in self.get_plugin_names():
      self.output.Debug(self, "Getting Plugin Configurations")
      self.load_plugin_configuration(key)
      self.map_config_functions(key)

  def get_plugin_names(self):
    #plugin names are the keys
    return self.plugin_dict.keys()

  def load_plugin_dict(self):
    self.output.Debug(self, "Load plugin dictionary")
    self.plugin_dict = {}
    doc_dir = os.path.join( os.path.dirname(__file__), "documents")
    doc_dirs = os.listdir(doc_dir)
    self.output.Debug(self, "Directories: %s" % str(doc_dirs))

    for d in doc_dirs:
      if not os.path.isdir(os.path.join(doc_dir, d)):
        continue

      self.output.Debug(self, "Working through: %s" % d)
      for path, dirs, files in os.walk(os.path.join(doc_dir, d)):
        for f in files:
          self.output.Debug(self, "\tFile: %s" % f)
          dpath = os.path.abspath(path)
          if os.path.exists(dpath + os.sep + "__init__.py") and f.endswith("py"):
            #Found a ptyhon file that is part of the package
            m = f.partition(".")[0]
            module_path = "nysa.gui.plugins.documents.%s.%s" % (d, m)
            self.output.Debug(self, "Module Path: %s" % module_path)
            res = __import__(module_path, fromlist=['*'])

            for name in dir(res):
              #look for the plugin_document subclass
              attr = getattr(res, name)
              if inspect.isclass(attr) and issubclass(attr, plugin_document.PluginDocument):
                self.plugin_dict[d] = {}
                self.plugin_dict[d]["module_path"] = module_path
                self.plugin_dict[d]["class"] = attr
                self.plugin_dict[d]["directory"] = dpath
                #get an instance of the class
                self.plugin_dict[d]["plugin"] = attr()
                self.plugin_dict[d]["plugin"].set_output(self.output)

      return self.plugin_dict

  def load_plugin_configuration(self, plugin_name, config_file_name = "config.json"):
    self.output.Debug(self, str("Reading the configuration file for %s" % plugin_name))
    xbuf = ""
    config_dict = {}
    config_path = os.path.join(self.plugin_dict[plugin_name]["directory"], config_file_name)
    self.output.Debug(self, str("Config file path: %s" % config_path))
    try:
      filein = open(config_path)
      self.output.Debug(self, "Opened the config file")
      config_dict = json.load(filein)

    except IOError as err:
      self.output.Error(self, str("File Not Found! %s" % str(err)))

    self.plugin_dict[plugin_name]["configuration"] = config_dict

  def map_config_functions(self, plugin_name):
    self.output.Debug(self, "in map_config_functions")
    pd = {}
    cd = self.plugin_dict[plugin_name]["configuration"]
    self.output.Debug(self, str("Configuration Dictionary for %s: %s" % (str(plugin_name), str(cd))))
    for key in cd.keys():
      if key == "functions":
        pd = cd[key]
    
    if pd is None:
      self.output.Debug(self, str("%s contains no funtions" % plugin_name))
      return None

    attr = dir(self.plugin_dict[plugin_name]["plugin"])
    self.output.Debug(self, str("Attributes %s" % str(attr)))

    #go through the configuration file functions and replace functions strins with functions
    for gui_type in pd.keys():
      self.output.Debug(self, "\tGUI Type: %s" % gui_type)
      for gui_comp in pd[gui_type].keys():
        self.output.Debug(self, "\t\tGUI Componets: %s" % gui_comp)
        for item in pd[gui_type][gui_comp].keys():
          if item == "function":
            func_name = pd[gui_type][gui_comp][item]
            self.output.Debug(self, "\t\t\tFunction: %s" % func_name)

            for a in attr:
              if func_name == str(a):
                func = getattr(self.plugin_dict[plugin_name]["plugin"], a)
                self.output.Debug(self, str("\t\t\tFound the attribute that matches: %s" % str(func)))
                #replace the name of the function with the ACTUAL FUNCTION!
                pd[gui_type][gui_comp][item] = func
                #pd[gui_type][gui_comp][item]()


    
