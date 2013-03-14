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
#from ..plugins import plugin_manager as pm


class WorkspaceManager ():

  def __init__(self):
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
    print "Hello"
    inspect.getfile(self)
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


