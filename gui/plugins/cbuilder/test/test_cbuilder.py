#! /usr/bin/python

import os
import sys
import wx
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))

from nysa.gui import nysa
from nysa.gui.plugins.cbuilder.cbuilder import CBuilder 

class TestFrame (wx.Frame):
  def __init__(self, parent, target):
    wx.Frame.__init__(self, None, wx.ID_ANY, "Test", size = (600, 400))
    print "Got the super init to work"
    self.tp  = wx.Panel(self)
    self.Show()


class CbuilderTest (unittest.TestCase):

  def setUp(self):
    print "setup"

  def test_hello(self):
    print "Hello world!"
    print str(self.__module__)
    self.assertEqual(0, 0)

  def test_panel(self):
    print "Test loading a panel with custom control"
    cb  = CBuilder()

    print "Creating a simple app"
    app = wx.PySimpleApp()
    frame = TestFrame(None, "Test")
    print "Got a test frame"
    cb.setup_main_view(frame.tp)

    app.MainLoop()


  def test_goodby(self):
    print "Goodby world!"
    self.assertEqual(0, 0)


if __name__ == "__main__":
  unittest.main()
