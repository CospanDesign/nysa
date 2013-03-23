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
from nysa.gui.plugins import plugin_manager

class WorkspaceManager ():
  output=None
  dbg = False
  pm  = None

  def __init__(self, output=None, dbg=False):
    self.dbg = dbg
    self.output = None
    self.pm = None
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
    self.load_plugins()

  def load_plugins (self):
    self.pm = plugin_manager.PluginManager()
    if self.pm.get_num_plugins() > 0:
      self.output.Debug (self, "Found Plugins:")
      for key in self.pm.get_plugin_names():
        self.output.Debug (self, str("\t%s" % key))


  def add_plugin_gui_components(self):
    #add the persistent components of the plugins
    #The plugin manager will give us a list of GUI components

    #add menu items
    #add toolbar items
    #add wizard
      #i suppose you don't really need to add this but it needs to be available :q



    pass

  def save_workspace  (self):
    pass

  def restore_workspace (self):
    pass

if __name__ == "__main__":
  wm = WorkspaceManager()
  os.chdir("../../..")
  print "dir: %s" % str(os.getcwd())
  from nysa.gui.main.workspace_manager import workspace_manager as wm

