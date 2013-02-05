#! /usr/bin/python

import wx
import wx.lib.agw.aui as aui
from main.nysa_status import NysaStatus
from main.nysa_status import StatusLevel
from main.nysa_navigator import NysaNavigator
from main.nysa_main import NysaMain

class Nysa (wx.App):
  '''Nysa App Class'''
  def __init__(self):
    wx.App.__init__(self)

  def OnInit(self):
    self.SetAppName("Nysa")
    self.main = NysaMain()
    self.main.Show()
    return True

  def getOutput(self):
    return self.main.getOutput()



if __name__ == "__main__":
  print "start"
  app = Nysa()
  app.MainLoop()
