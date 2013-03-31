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

import wx
import inspect
import os
import sys
import main_status
from main_status import StatusLevel

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

from nysa.gui.plugins.plugin_manager import PluginManager

class WorkspaceManager ():
  output=None
  dbg = False
  _pm = None
  view = None
  projects = {}
  project_types = {}
  id_map = {}


  def __init__(self, view=None, pm=None, output=None,  dbg=False):
    self.dbg = dbg
    self.output = None
    self.pgl = None
    self._pm = pm
    self.view=view

    if output is None:
      self.output = main_status.Dummy()
      if self.dbg:
        self.output.SetLevel(StatusLevel.VERBOSE)
      else:
        self.output.SetLevel(StatusLevel.INFO)
    else:
      self.output = output

    '''
    self.cfg = Config('nysa')
    #Config Functions
    bool_value = self.cfg.Exists(key)
    string_value = self.cfg.Read(key, default_value)
    int_value = self.cfg.ReadInt(key, default_value)
    float_value = self.cfg.ReadFloat(key, default_value)
    bool_value = self.cfg.ReadBool(key, default_value)
    self.cfg.Write(key, value)
    self.cfg.WriteInt(key, value)
    self.cfg.WriteFloat(key, value)
    self.cfg.WriteBool(key, value)
    '''
    self.output.Debug(self, "Started")
    if pm is not None:
      self.load_projects_menu_items()

    else:
      self.output.Error(self, "Project manager is not loaded")

  def save_workspace  (self):
    pass

  def restore_workspace (self):
    pass

  def load_projects_menu_items(self):
    #by now I should have the plugin manager reference
    self.project_types = {}
    plugins = self._pm.get_plugin_names()
    for p in plugins:
      proj_names = self._pm.get_project_reference(p)
      for pp in proj_names:
        if pp not in self.project_types.keys():
          self.project_types[pp] = {}
        self.project_types[pp]["plugin"] = p
        name = self._pm.get_project_name(p, pp)
        self.project_types[pp]["name"] = name
        self.output.Info(self, "Loading: %s from plugin %s" % (pp, p))
        mid = self.view.add_menu_item(str("Workspace.%s.%s" % (p, name)), "Add new project", None, self.new_project, self.project_types[pp])
        self.project_types[pp]
        self.output.Info(self, "ID %d maps to %s" % (mid, pp))
        self.id_map[mid] = (p, pp)
        

  def new_project(self, evt):
    self.output.Info(self, str("User selected a project to open: ID = %d"% evt.GetId()))
    plugin_name, project_reference = self.id_map[evt.GetId()]
    self.output.Info(self, str("Plugin:Project: %s:%s" % (plugin_name, project_reference)))


    #call the custom 'new project' settings from plugin_project
    clazz = self._pm.get_project_class(plugin_name, project_reference)

    name      = "New Project"
    temp_name = "New Project"
    val       = 0
    while temp_name in self.projects.keys():
      val + 1
      temp_name = name + str(val)

    #self.output.Info(self, str("Keys of the project types of %s are %s" % (project_reference, self.project_types[project_reference].keys())))
    self.projects[temp_name] = clazz(output = self.output, name = name)

    self.projects[temp_name].new_project()

    self.update_workspace()

  def on_add_workspace(self):
    pass

  def on_change_workspace(self):
    pass

  def update_workspace(self):
    #update any changes to the workspace
    pass

if __name__ == "__main__":
  wm = WorkspaceManager()
  os.chdir("../../..")
  print "dir: %s" % str(os.getcwd())
  from nysa.gui.main.workspace_manager import workspace_manager as wm

