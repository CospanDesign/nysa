#! /usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
#print "Append: %s" % str(os.path.join(os.path.dirname(__file__), os.pardir))
#import nysa

import wx
import wx.lib.agw.aui as aui
from main.main_status import MainStatus
from main.main_status import StatusLevel
from main.main_navigator import MainNavigator
from main.workspace_manager import WorkspaceManager
from main.nysa_main import NysaMain

class NysaGui (wx.App):
  '''Nysa App Class'''
  _wm = None
  output = None

  def __init__(self):
    wx.App.__init__(self)

  def OnInit(self):
    self.SetAppName("Nysa")
    self.main = NysaMain()
    #load the workspace manager
    self.output = self.getOutput()
    self._wm = WorkspaceManager(self.main.getOutput())
    self.main.Show()
    self.loadPlugins()
    return True


  def loadPlugins(self):
    self.output.Verbose (self, "Loading Plugins...")

  def getOutput(self):
    return self.main.getOutput()

if __name__ == "__main__":
  #print "start"
  app = NysaGui()
  app.MainLoop()
