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



class PluginManager ():
  def __init__(self):
    pass

  def get_plugin_dict(self):
    plugin_dict = {}
    parent_dir = os.path.dirname(__file__)
    parent_dirs = os.listdir(parent_dir)
    for d in parent_dirs:
      if os.path.isdir(os.path.join(parent_dir,d)):
        for (path, dirs, files) in os.walk( os.path.join(parent_dir, d)):
          if len(dirs) > 0:
            for f in files:
              dpath = os.path.abspath(path)
              if os.path.exists (dpath + os.sep + "__init__.py") and f.endswith("py"):
                m = f.partition(".")[0]
                module_path = "nysa.gui.plugins.%s.%s" % (d, m)
                res = __import__(module_path, fromlist=['*'])

                for name in dir(res):
                  attr = getattr(res, name)
                  if inspect.isclass(attr) and issubclass(attr, plugin.Plugin):
                    plugin_dict[d] = [module_path, attr, dpath]
                    print "Class %s" % str(attr)

    return plugin_dict

  def get_plugin_class(self, plugin_name):
    plugin_dict = self.get_plugin_dict()
    print "plugin_dict %s" % str(plugin_dict)
    clazz = plugin_dict[plugin_name][1]
    print "clazz: %s" % str(clazz)
    clazz.path = plugin_dict[plugin_name][2]
    return clazz

