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
import plugin
import json

#print "directory: %s" % str(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir))

from nysa.gui.main import main_status
from nysa.gui.main.main_status import StatusLevel

class PluginManager ():
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

    self.load_plugin_dict()
    for key in self.get_plugin_names():
      self.load_plugin_configuration(key)
      self.map_persistent_functions(key)

  def get_plugin_names(self):
    #plugin names are the keys
    return self.plugin_dict.keys()

  def get_num_plugins(self):
    return len(self.plugin_dict.keys())

  def load_plugin_dict(self):
    self.plugin_dict = {}
    parent_dir = os.path.dirname(__file__)
    parent_dirs = os.listdir(parent_dir)
    for d in parent_dirs:
      #for each of the directories search the files for one that uses the plugin class
      if os.path.isdir(os.path.join(parent_dir,d)):
        for (path, dirs, files) in os.walk( os.path.join(parent_dir, d)):
          if len(dirs) > 0:
            for f in files:
              dpath = os.path.abspath(path)
              if os.path.exists (dpath + os.sep + "__init__.py") and f.endswith("py"):
                #if the file isa python file and it is part of the package
                m = f.partition(".")[0]
                module_path = "nysa.gui.plugins.%s.%s" % (d, m)
                res = __import__(module_path, fromlist=['*'])

                for name in dir(res):
                  attr = getattr(res, name)
                  if inspect.isclass(attr) and issubclass(attr, plugin.Plugin):
                    self.plugin_dict[d] = {}
                    self.plugin_dict[d]["module_path"] = module_path
                    self.plugin_dict[d]["class"] = attr
                    self.plugin_dict[d]["directory"] = dpath
                    #get an instance of the class
                    self.plugin_dict[d]["plugin"] = attr()
    return self.plugin_dict

  def load_plugin_configuration(self, plugin_name, config_file_name="config.json"):
    self.output.Debug(self, str("Reading the configuration file for %s" % plugin_name))
    xbuf = ""
    config_dict = {}
    config_path = os.path.join (self.plugin_dict[plugin_name]["directory"], config_file_name)
    self.output.Debug(self, str("Config file path: %s" % config_path))
    try:
      filein = open(config_path)
      self.output.Debug(self, "Opened the config file")
      config_dict = json.load(filein)
    except IOError as err:
      self.output.Error(self, str("File Not Found! %s " % str(err)))

    self.plugin_dict[plugin_name]["configuration"] = config_dict

  def map_persistent_functions(self, plugin_name):
    self.output.Debug(self, "in map_persistent_functions")
    pd = {}
    cd = self.plugin_dict[plugin_name]["configuration"]
    self.output.Debug(self, str("Configuration Dictionary for %s: %s" % (str(plugin_name), str(cd))))
    #p_type  = None
    #look for the persistent key
    for key in cd.keys():
      if key == "persistent":
        #get the persistent dictionary
        pd = cd[key]
    if pd is None:
      self.output.Debug (self, str("%s contains no persistent functions" %plugin_name))
      #no persistent functions in this plugin
      return None

    attr = dir(self.plugin_dict[plugin_name]["plugin"])
    self.output.Debug(self, str("Attributes %s" % str(attr)))

    #go through the configuration file persistent items and replace the function strings with functions
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

            
    
    

  def get_plugin_path(self, plugin_name):
    return self.plugin_dict[plugin_name]["module_path"]

  def get_plugin_class(self, plugin_name):
    self.output.Debug(self, str ("plugins %s" % str (self.plugin_dict.keys())))
    clazz = self.plugin_dict[plugin_name]["class"]
    clazz.path = self.plugin_dict[plugin_name]["directory"]
    return clazz

    #find all the persistent items
    for key in p_dict.keys():
      #if "type" in p_dict[key].keys():
      #  self.output.Debug(self, str("Found persistent type: %s" % p_dict[key]["type"]))
      #get an reference to the plugin module
      print "dir %s" % str(self)



